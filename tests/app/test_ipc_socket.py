import pytest
from pytest_mock import MockerFixture

from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.ipc_socket import UISocket
from savegem.common.core.ipc_socket import IPCProp, IPCCommand


@pytest.fixture(autouse=True)
def _setup(module_patch, app_context, games_config, prop_mock, logger_mock, activity_mock, app_state_mock, gui_mock):
    """
    Mocks all external dependencies and singletons used by UISocket.
    """

    games_config.is_auto_mode = True
    prop_mock.return_value = 12345


@pytest.fixture
def _ui_socket(mocker: MockerFixture, ipc_socket_base_init_mock, gdrive_watcher_socket_mock,
               process_watcher_socket_mock):
    """
    Creates a fresh UISocket instance for each test.
    """

    ipc_socket_base_init_mock.reset_mock()

    # Creating a new instance for the test
    ui_socket = UISocket()

    # Mock the 'send' method inherited from IPCSocket
    ui_socket.send = mocker.MagicMock()
    return ui_socket


def test_ui_socket_init(mocker: MockerFixture, _ui_socket, ipc_socket_base_init_mock, gdrive_watcher_socket_mock,
                        process_watcher_socket_mock):
    """
    Tests that UISocket initializes the base class with the correct port
    and registers the correct child processes.
    """

    # Base IPCSocket.__init__ should be called with the mocked port
    ipc_socket_base_init_mock.assert_called_once_with(mocker.ANY, 12345)

    # Check that the internal list of child processes is correct
    child_processes = _ui_socket._UISocket__child_processes  # noqa
    assert len(child_processes) == 2
    assert gdrive_watcher_socket_mock in child_processes
    assert process_watcher_socket_mock in child_processes


def test_send_ui_refresh_command(_ui_socket):
    """
    Tests that send_ui_refresh_command formats the IPC message correctly.
    """

    event_name = "TestEvent"

    _ui_socket.send_ui_refresh_command(event_name)

    expected_message = {
        IPCProp.Command: IPCCommand.RefreshUI,
        IPCProp.Event: event_name
    }

    _ui_socket.send.assert_called_once_with(expected_message)  # noqa


def test_notify_children(_ui_socket, gdrive_watcher_socket_mock, process_watcher_socket_mock):
    """
    Tests that notify_children sends the message to all registered child sockets.
    """

    test_message = {
        IPCProp.Command: IPCCommand.RefreshUI
    }

    _ui_socket.notify_children(test_message)

    gdrive_watcher_socket_mock.send.assert_called_once_with(test_message)
    process_watcher_socket_mock.send.assert_called_once_with(test_message)


def test_handle_refresh_auto_mode_disabled(_ui_socket, app_state_mock, games_config, activity_mock, gui_mock):
    """
    Tests that if auto mode is disabled, only the final GUI refresh is called,
    and no data refresh calls are made.
    """

    # Set auto mode to False
    app_state_mock.is_auto_mode = False

    _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: UIRefreshEvent.CloudSaveFilesChange})

    # Assert mutex usage
    gui_mock.mutex.lock.assert_called_once()
    gui_mock.mutex.unlock.assert_called_once()

    # Assert refresh calls are skipped
    games_config.refresh.assert_not_called()
    games_config.download.assert_not_called()
    games_config.current.meta.drive.refresh.assert_called_once()
    activity_mock.refresh.assert_not_called()

    # Assert final GUI refresh is called
    gui_mock.refresh.assert_called_once_with(UIRefreshEvent.CloudSaveFilesChange)


def test_handle_refresh_auto_mode_enabled_base_calls(_ui_socket, app_state_mock, games_config, gui_mock):
    """
    Tests that if auto mode is enabled, app.games.refresh() is always called
    regardless of the specific event type.
    """

    event_name = 'SomeOtherEvent'

    # Set auto mode to True (default, but explicit for clarity)
    app_state_mock.is_auto_mode = True

    _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: event_name})

    # Assert games.refresh is called
    games_config.refresh.assert_called_once()

    # Assert final GUI refresh is called
    gui_mock.refresh.assert_called_once_with(event_name)


def test_handle_refresh_game_config_change(_ui_socket, app_state_mock, games_config, activity_mock):
    """
    Tests the logic for UIRefreshEvent.GameConfigChange.
    """

    app_state_mock.is_auto_mode = True

    _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: UIRefreshEvent.GameConfigChange})

    # Assert specific refresh calls for GameConfigChange
    games_config.download.assert_called_once()
    games_config.current.meta.drive.refresh.assert_called_once()

    # Assert other event calls are skipped
    activity_mock.refresh.assert_not_called()


def test_handle_refresh_activity_log_update(_ui_socket, app_state_mock, games_config, activity_mock):
    """
    Tests the logic for UIRefreshEvent.ActivityLogUpdate.
    """

    app_state_mock.is_auto_mode = True

    _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: UIRefreshEvent.ActivityLogUpdate})

    # Assert specific refresh calls for ActivityLogUpdate
    activity_mock.refresh.assert_called_once()

    # Assert other event calls are skipped
    games_config.download.assert_not_called()
    games_config.current.meta.drive.refresh.assert_not_called()


def test_handle_refresh_cloud_save_files_change(_ui_socket, app_state_mock, games_config, activity_mock):
    """
    Tests the logic for UIRefreshEvent.CloudSaveFilesChange.
    """

    app_state_mock.is_auto_mode = True

    _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: UIRefreshEvent.CloudSaveFilesChange})

    # Assert specific refresh calls for CloudSaveFilesChange
    games_config.current.meta.drive.refresh.assert_called_once()

    # Assert other event calls are skipped
    games_config.download.assert_not_called()
    activity_mock.refresh.assert_not_called()


def test_handle_non_refresh_command_is_ignored(_ui_socket, gui_mock, games_config):
    """
    Tests that a command other than RefreshUI is ignored by _handle.
    """

    _ui_socket._handle(IPCCommand.StateChanged, {'SomeProp': 'Value'})

    # Assert no processing occurred
    gui_mock.mutex.lock.assert_not_called()
    games_config.refresh.assert_not_called()
    gui_mock.refresh.assert_not_called()


def test_handle_mutex_unlock_on_exception(_ui_socket, gui_mock, app_state_mock, games_config):
    """
    Tests that the mutex is always unlocked, even if an exception occurs during processing.
    """

    # Make one of the required functions raise an exception
    games_config.refresh.side_effect = Exception("Test Error")
    app_state_mock.is_auto_mode = True

    with pytest.raises(Exception, match="Test Error"):
        _ui_socket._handle(IPCCommand.RefreshUI, {IPCProp.Event: UIRefreshEvent.CloudSaveFilesChange})

    # Assert mutex was locked and then unlocked
    gui_mock.mutex.lock.assert_called_once()
    gui_mock.mutex.unlock.assert_called_once()

    # Assert GUI refresh was NOT called since it was inside the try block
    gui_mock.refresh.assert_not_called()
