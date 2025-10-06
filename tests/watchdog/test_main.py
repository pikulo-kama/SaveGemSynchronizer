import pytest
from pytest_mock import MockerFixture

import subprocess
from unittest.mock import MagicMock

from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder
from savegem.watchdog.main import Watchdog
from savegem.common.service.daemon import Daemon, ExitTestLoop


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture):
    """Mocks Daemon's __init__ to inject required attributes into Watchdog."""

    # Function that replaces the original Daemon.__init__ call
    def mock_daemon_init(self, service_name, requires_auth):
        # Set the attributes Watchdog relies on from its parent
        self.__service_name = service_name
        self.__requires_auth = requires_auth
        self.__interval = 1.0  # Default interval for testing
        self._logger = MagicMock()

    # Patch the __init__ method of the Daemon class.
    # The patch target is the Daemon class itself.
    mocker.patch.object(Daemon, '__init__', side_effect=mock_daemon_init)


@pytest.fixture
def mock_config():
    """Fixture for configuration with sample child processes."""
    return MockJsonConfigHolder({
        "childProcesses": [
            "FirstService.exe",
            "_SecondService.exe",
            "third_service.exe"
        ]
    })


@pytest.fixture
def _watchdog():
    """Fixture for the Watchdog instance."""

    watchdog = Watchdog()
    watchdog.interval = 1.0

    return watchdog


@pytest.fixture
def mock_subprocess(mocker: MockerFixture):
    """Fixture to mock subprocess.Popen and its returned process object."""
    # Mock the process instance returned by Popen
    mock_process = mocker.MagicMock()
    mock_process.wait.return_value = 0  # Assume clean exit by default

    # Mock Popen to return the mock process instance
    popen_mock = mocker.patch.object(subprocess, 'Popen', return_value=mock_process)
    return popen_mock, mock_process


@pytest.fixture
def _thread_mock(module_patch):
    return module_patch("threading.Thread", autospec=True)


def test_initialize_starts_threads(_watchdog, mock_config, _thread_mock, mocker: MockerFixture):
    """Test that _initialize registers commands and starts a thread for each."""

    # Act
    _watchdog._initialize(mock_config)

    # Assert
    expected_commands = mock_config.get_value("childProcesses")

    # 2. Check that Thread was called once for each command
    assert _thread_mock.call_count == len(expected_commands)

    # 3. Check arguments: target should be __watch_process, and args should be the command string
    expected_calls = [
        mocker.call(
            target=_watchdog._Watchdog__watch_process,  # noqa
            args=(cmd,),
            daemon=True
        ) for cmd in expected_commands
    ]

    _thread_mock.assert_has_calls(expected_calls, any_order=True)
    _thread_mock.return_value.start.call_count = 3


def test_watch_process_success_path(_watchdog, mock_subprocess, time_sleep_mock):
    """Test process starts, exits cleanly (0), and prepares for restart."""
    popen_mock, mock_process = mock_subprocess
    command_args = ["echo", "hello", "world"]

    # Configure wait to return a specific exit code
    mock_process.wait.return_value = 143  # Mock process terminated signal
    mock_process.wait.side_effect = [None, ExitTestLoop()]

    with pytest.raises(ExitTestLoop):
        _watchdog._Watchdog__watch_process(command_args)  # noqa

    popen_mock.call_count = 2
    popen_mock.assert_called_with(command_args)

    mock_process.wait.call_count = 2
    _watchdog._logger.info.call_count = 2

    _watchdog._logger.info.assert_called()
    _watchdog._logger.error.assert_called_once()

    time_sleep_mock.assert_called_once()


def test_watch_process_file_not_found_error(_watchdog, mock_subprocess):
    """Test process handles FileNotFoundError when executable is missing."""

    popen_mock, _ = mock_subprocess
    command_args = ["missing_executable", "--arg"]
    popen_mock.side_effect = [FileNotFoundError(2, "No such file or directory: 'missing_executable'"), ExitTestLoop()]

    with pytest.raises(ExitTestLoop):
        _watchdog._Watchdog__watch_process(command_args)  # noqa

    popen_mock.call_count = 2
    popen_mock.assert_called_with(command_args)

    _watchdog._logger.error.assert_called_once()


def test_watch_process_unhandled_exception(_watchdog, mock_subprocess):
    """Test process handles generic unhandled exceptions during execution."""
    popen_mock, _ = mock_subprocess
    command_string = "echo test"

    # Mock Popen to raise a generic error
    popen_mock.side_effect = [PermissionError("Access denied"), ExitTestLoop()]

    # Act
    with pytest.raises(ExitTestLoop):
        _watchdog._Watchdog__watch_process(command_string)  # noqa

    # Assert
    # 1. Correct unhandled error logging
    _watchdog._logger.error.assert_called_once()  # noqa
    assert "Error in watchdog" in _watchdog._logger.error.call_args[0][0]
    assert "Access denied" in _watchdog._logger.error.call_args[0][1].args[0]
