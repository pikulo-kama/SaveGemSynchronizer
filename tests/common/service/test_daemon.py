from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def _mock_daemon():
    from savegem.common.service.daemon import Daemon

    class MockDaemon(Daemon):
        """
        A concrete implementation of Daemon for testing purposes.
        """

        def __init__(self, service_name, requires_auth, config_present=True):
            self._config_present = config_present
            super().__init__(service_name, requires_auth)

        def _work(self):
            """
            Simulate the main daemon work.
            """

            self._logger.info("Working...")
            pass

        def _initialize(self, config: MagicMock):
            """
            Used to test if _initialize is called.
            """

            self.initialized = True
            self._logger.debug("MockDaemon initialized.")

    return MockDaemon


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture, json_config_holder_mock):

    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder

    mock_holder = MockJsonConfigHolder({
        "processName": "test_mock_process",
        "iterationIntervalSeconds": 10  # Non-default interval
    })

    mocker.spy(mock_holder, "get_value")
    json_config_holder_mock.return_value = mock_holder


@pytest.fixture
def mock_sys_exit(mocker: MockerFixture):
    """
    Mock 'sys.exit' to prevent the process from exiting.
    """
    return mocker.patch("sys.exit")


def test_daemon_init_with_config(module_patch, path_exists_mock, json_config_holder_mock, _mock_daemon):
    """
    Test successful initialization when config file is present.
    """

    from savegem.common.service.daemon import Daemon

    path_exists_mock.return_value = True

    daemon = _mock_daemon("TestService", requires_auth=False)

    assert daemon.interval == 10  # Should use the value from mocked config
    assert daemon.initialized is True

    json_config_holder_mock.assert_called_once()
    json_config_holder_mock.return_value.get_value.assert_any_call("processName")
    json_config_holder_mock.return_value.get_value.assert_any_call("iterationIntervalSeconds", Daemon.DefaultInterval)


def test_daemon_init_without_config(module_patch, path_exists_mock, _mock_daemon):
    """
    Test initialization when config file is missing.
    """

    from savegem.common.service.daemon import Daemon

    path_exists_mock.return_value = False
    mock_config_constructor = module_patch("JsonConfigHolder")

    daemon = _mock_daemon("TestService", requires_auth=False, config_present=False)

    assert daemon.interval == Daemon.DefaultInterval
    assert not hasattr(daemon, 'initialized')
    mock_config_constructor.assert_not_called()


def test_daemon_init_process_already_running(module_patch, path_exists_mock, mock_sys_exit, _mock_daemon):
    """
    Test that the daemon exits if another instance is running.
    """

    path_exists_mock.return_value = True
    is_process_running = module_patch("is_process_already_running", return_value=True)
    # We expect sys.exit(0) to be called during initialization
    _mock_daemon("TestService", requires_auth=False)

    is_process_running.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)


def test_daemon_start_work_loop_no_auth(mocker: MockerFixture, path_exists_mock, time_sleep_mock, _mock_daemon):
    """
    Test the main loop when no authentication is required.
    """

    from savegem.common.service.daemon import ExitTestLoop

    path_exists_mock.return_value = False
    daemon = _mock_daemon("TestService", requires_auth=False)

    # Mock _work to raise an exception after 1 call to break the loop
    daemon._work = mocker.Mock(side_effect=[None, ExitTestLoop])

    with pytest.raises(ExitTestLoop):
        daemon.start()

    # Should call _work twice (once for the None return, once for the ExitTestLoop)
    assert daemon._work.call_count == 2  # noqa
    # Should call time.sleep once after the first work and once after the second (before the exception)
    assert time_sleep_mock.call_count == 1


def test_daemon_start_auth_required_delayed(mocker: MockerFixture, resolve_app_data_mock, path_exists_mock,
                                            module_patch, time_sleep_mock, logger_mock, _mock_daemon):
    """
    Test the loop when authentication is required and delayed.
    """

    from savegem.common.service.daemon import ExitTestLoop

    resolve_app_data_mock.return_value = "/mock/appdata/gdrive_token.txt"
    path_exists_mock.side_effect = [False, False, True, ExitTestLoop]

    daemon = _mock_daemon("AuthService", requires_auth=True)

    # Mock _work to ensure it's not called until auth is complete
    daemon._work = mocker.Mock()

    with pytest.raises(ExitTestLoop):
        daemon.start()

    # The side_effect of os.path.exists determines the flow:
    # 1. Loop 1: os.path.exists -> False (Auth not done, calls time.sleep)
    # 2. Loop 2: os.path.exists -> False (Auth not done, calls time.sleep)
    # 3. Loop 3: os.path.exists -> True (Auth done, calls _work)
    # 4. Loop 4: os.path.exists -> ExitTestLoop (Breaks the loop)

    assert logger_mock.debug.call_count == 1
    logger_mock.debug.assert_any_call(
        "Authentication has not been completed. Sleeping for %d second(s).", daemon.interval
    )

    assert daemon._work.call_count == 1  # noqa
    assert time_sleep_mock.call_count == 2


def test_daemon_start_work_exception_handling(mocker: MockerFixture, resolve_app_data_mock, path_exists_mock,
                                              time_sleep_mock, logger_mock, _mock_daemon):
    """
    Test that exceptions in _work are logged and the loop continues.
    """

    from savegem.common.service.daemon import ExitTestLoop

    resolve_app_data_mock.return_value = "/mock/appdata/gdrive_token.txt"
    path_exists_mock.return_value = False

    daemon = _mock_daemon("ErrorService", requires_auth=False)

    # Mock _work to raise an exception on the first call, then break on the second
    daemon._work = mocker.Mock(side_effect=[TypeError("Mock Error"), ExitTestLoop])

    with pytest.raises(ExitTestLoop):
        daemon.start()

    assert daemon._work.call_count == 2  # noqa

    # Check that the error was logged
    logger_mock.error.assert_called_once()
    logger_mock.error.assert_called_with(
        "Exception in '%s' service: %s", "ErrorService", mocker.ANY, exc_info=True
    )

    # time.sleep should be called after the exception is handled
    assert time_sleep_mock.call_count == 1
