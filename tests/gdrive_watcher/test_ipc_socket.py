import pytest


@pytest.fixture(autouse=True)
def _setup(prop_mock):
    """
    Mocks external dependencies used by GdriveWatcherSocket.
    """
    prop_mock.return_value = 54321


@pytest.fixture
def _ipc_socket_mock(module_patch, prop_mock):
    return module_patch("IPCSocket.__init__", return_value=None)


def test_init_calls_parent_with_correct_port(_ipc_socket_mock, prop_mock):
    """
    Test GdriveWatcherSocket initializes the base class with the port from prop().
    """

    from savegem.gdrive_watcher.ipc_socket import GdriveWatcherSocket

    # Arrange
    expected_port = 54321
    _ipc_socket_mock.return_value = expected_port

    # Act
    GdriveWatcherSocket()

    # Assert
    prop_mock.assert_called_once_with("ipc.gdriveWatcherSocketPort")
    _ipc_socket_mock.assert_called_once_with(expected_port)


def test_handle_gui_initialized_command_saves_flag_file(_ipc_socket_mock, save_file_mock, resolve_temp_file_mock):
    """
    Test that the GUIInitialized command triggers the flag file creation.
    """

    from constants import File
    from savegem.common.core.ipc_socket import IPCCommand
    from savegem.gdrive_watcher.ipc_socket import GdriveWatcherSocket

    socket_instance = GdriveWatcherSocket()

    mock_flag_path = "/mock/temp/gui_flag.txt"
    resolve_temp_file_mock.return_value = mock_flag_path

    socket_instance._handle(IPCCommand.GUIInitialized, {})

    resolve_temp_file_mock.assert_called_once_with(File.GUIInitializedFlag)
    save_file_mock.assert_called_once_with(mock_flag_path, "")


@pytest.mark.parametrize("command", [
    "UnknownCommand",
    "SOME_OTHER_COMMAND",
    "status_check"
])
def test_handle_other_commands_does_nothing(_ipc_socket_mock, save_file_mock, command):
    """
    Test that commands other than GUIInitialized do not trigger file saving.
    """

    from savegem.gdrive_watcher.ipc_socket import GdriveWatcherSocket

    socket_instance = GdriveWatcherSocket()

    socket_instance._handle(command, {"data": 123})

    save_file_mock.assert_not_called()
