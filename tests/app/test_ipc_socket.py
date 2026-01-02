from pytest_mock import MockerFixture
from unittest.mock import call
import pytest

from tests.test_data import ConfigTestData


class TestUISocket:

    @pytest.fixture
    def _refresh_ui_mock(self, module_patch):
        return module_patch("UISocket.refresh_ui")


    @pytest.fixture
    def _rebuild_window_mock(self, module_patch):
        return module_patch("UISocket.rebuild_window")


    def test_ui_socket_init_calls_parent_init(self, ipc_socket_base_init_mock, prop_mock):
        """
        Tests that __init__ calls IPCSocket and QObject constructors
        and sets up the child process list.
        """

        from savegem.app.ipc_socket import UISocket

        prop_mock.side_effect = lambda key: 12345 if key == "ipc.uiSocketPort" else None

        UISocket()

        assert ipc_socket_base_init_mock.call_args[0][1] == 12345
        prop_mock.assert_called_once_with("ipc.uiSocketPort")


    def test_send_ui_refresh_command_sends_correct_message(self, mocker: MockerFixture, ui_socket_mock):
        """
        Tests that send_ui_refresh_command formats and sends the correct message.
        """

        from savegem.app.ipc_socket import UISocket, IPCCommand
        from savegem.common.core.ipc_socket import IPCProp

        event = "TestEvent"
        socket = UISocket()
        socket.send = mocker.Mock()

        socket.send_ui_refresh_command(event)

        # Check that the send method was called with
        # the correct dictionary structure
        expected_message = {
            IPCProp.Command: IPCCommand.RefreshUI,
            IPCProp.Event: event
        }

        socket.send.assert_called_once_with(expected_message)  # noqa


    def test_handle_rebuild_window_emits_signal(self, _refresh_ui_mock, _rebuild_window_mock):
        """
        Tests handling of IPCCommand.RebuildWindow.
        """

        from savegem.app.ipc_socket import UISocket
        from savegem.common.core.ipc_socket import IPCCommand

        socket = UISocket()

        socket._handle(IPCCommand.RebuildWindow, {})

        _rebuild_window_mock.emit.assert_called_once()
        _refresh_ui_mock.emit.assert_not_called()


    def test_handle_refresh_ui_activity_log(self, mocker: MockerFixture, _refresh_ui_mock):
        """
        Tests handling of IPCCommand.RefreshUI for ActivityLogUpdate.
        """

        from savegem.app.ipc_socket import UISocket
        from savegem.app.gui.constants import UIRefreshEvent
        from savegem.common.core.ipc_socket import IPCCommand, IPCProp

        mock_update_activity = mocker.patch.object(UISocket, '_UISocket__update_activity')

        socket = UISocket()
        socket._handle(IPCCommand.RefreshUI, {
            IPCProp.Event: UIRefreshEvent.ActivityLogUpdate
        })

        # Check internal update logic
        mock_update_activity.assert_called_once()

        # Check signal emission
        _refresh_ui_mock.emit.assert_called_once_with(UIRefreshEvent.ActivityLogUpdate)


    def test_handle_refresh_ui_game_config_change(self, mocker: MockerFixture, _refresh_ui_mock):
        """
        Tests handling of IPCCommand.RefreshUI for GameConfigChange.
        """

        from savegem.app.ipc_socket import UISocket
        from savegem.app.gui.constants import UIRefreshEvent
        from savegem.common.core.ipc_socket import IPCCommand, IPCProp

        mock_update_games = mocker.patch.object(UISocket, '_UISocket__update_games_configuration')

        socket = UISocket()
        socket._handle(IPCCommand.RefreshUI, {
            IPCProp.Event: UIRefreshEvent.GameConfigChange
        })

        # Check internal update logic
        mock_update_games.assert_called_once_with(UIRefreshEvent.GameConfigChange)

        # Check signal emission
        _refresh_ui_mock.emit.assert_called_once_with(UIRefreshEvent.GameConfigChange)


    def test_handle_unknown_command(self, _refresh_ui_mock, _rebuild_window_mock):
        """
        Tests handling of an unknown IPC command.
        """

        from savegem.app.ipc_socket import UISocket

        socket = UISocket()
        socket._handle("UnknownCommand", {})

        _rebuild_window_mock.emit.assert_not_called()
        _refresh_ui_mock.emit.assert_not_called()


    def test_notify_children_sends_message_to_all_children(self, gdrive_watcher_socket_mock,
                                                           process_watcher_socket_mock, logger_mock):
        """
        Tests that notify_children sends the message to all configured child sockets.
        """

        from savegem.app.ipc_socket import UISocket

        message = {"Command": "TestMessage"}
        gdrive_watcher_socket_mock.port = 10001
        process_watcher_socket_mock.port = 10002

        socket = UISocket()
        socket.notify_children(message)

        # Check calls to the two child sockets
        gdrive_watcher_socket_mock.send.assert_called_once_with(message)
        process_watcher_socket_mock.send.assert_called_once_with(message)

        # Check logging
        logger_mock.debug.assert_has_calls([
            call("Sending message to child processes."),
            call("Sent message to socket on port %d", 10001),
            call("Sent message to socket on port %d", 10002)
        ], any_order=False)


    def test_internal_update_activity(self, holder_mock, activity_mock):
        """
        Tests __update_activity logic.
        """

        from savegem.app.ipc_socket import UISocket
        from savegem.constants import HolderObject

        # Call the static method directly
        UISocket._UISocket__update_activity()  # noqa

        # Check data download
        holder_mock.download_json.assert_called_once_with(
            HolderObject.Activity, ConfigTestData.ActivityLogFileId
        )

        # Check app refresh
        activity_mock.refresh.assert_called_once()


    def test_internal_update_games_config_change(self, holder_mock, games_config_mock):
        """
        Tests __update_games_configuration logic when GameConfigChange event occurs.
        """

        from savegem.app.ipc_socket import UISocket, UIRefreshEvent
        from savegem.constants import HolderObject

        UISocket._UISocket__update_games_configuration(UIRefreshEvent.GameConfigChange)  # noqa

        # 1. Check service_info download and initialization (since event is GameConfigChange)
        holder_mock.download_json.assert_called_once_with(
            HolderObject.GamesConfig, ConfigTestData.GameConfigFileId
        )
        games_config_mock.initialize.assert_called_once()

        # 2. Check per-game logic
        for game_mock in games_config_mock:
            game_mock.meta.local.calculate_checksum.assert_called_once()
            game_mock.meta.drive.refresh.assert_called_once()

        # 3. Check auto-mode reload (only for the first game, which is mocked with auto_mode=True)
        games_config_mock.first.meta.local.refresh.assert_called_once()
        games_config_mock.second.meta.local.refresh.assert_not_called()


    def test_internal_update_cloud_save_files_change(self, holder_mock, games_config_mock):
        """
        Tests __update_games_configuration logic when CloudSaveFilesChange event occurs.
        """

        from savegem.app.ipc_socket import UISocket
        from savegem.app.gui.constants import UIRefreshEvent

        UISocket._UISocket__update_games_configuration(UIRefreshEvent.CloudSaveFilesChange)  # noqa

        # 1. Check service_info download/init is skipped (since event is NOT GameConfigChange)
        holder_mock.download_json.assert_not_called()
        games_config_mock.initialize.assert_not_called()

        # 2. Check per-game logic is still executed
        for game_mock in games_config_mock:
            game_mock.meta.local.calculate_checksum.assert_called_once()
            game_mock.meta.drive.refresh.assert_called_once()

        games_config_mock.first.meta.local.refresh.assert_called_once()
        games_config_mock.second.meta.local.refresh.assert_not_called()
