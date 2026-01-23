from PyQt6.QtCore import pyqtSignal, QObject
from kui.core.shortcut import prop, add_dynamic_data
from kutil.logger import get_logger

from src.savegem.constants import HolderObject
from src.savegem.constants import UIRefreshEvent
from src.savegem.common.core.context import context
from src.savegem.common.core.ipc_socket import IPCSocket, IPCCommand, IPCProp
from src.savegem.common.service.gdrive import GDrive
from src.savegem.gdrive_watcher.ipc_socket import google_drive_watcher_socket
from src.savegem.process_watcher.ipc_socket import process_watcher_socket

_logger = get_logger(__name__)


class UISocket(IPCSocket, QObject):

    refresh_ui = pyqtSignal(str)
    rebuild_window = pyqtSignal()

    def __init__(self):
        IPCSocket.__init__(self, prop("ipc.ui-socket-port"))
        QObject.__init__(self)

        self.__child_processes = [google_drive_watcher_socket, process_watcher_socket]

    def send_ui_refresh_command(self, event: str):
        """
        Used to send refresh event
        to UI socket.
        """

        self.send({
            IPCProp.Command: IPCCommand.RefreshUI,
            IPCProp.Event: event
        })

    def _handle(self, command: str, message: dict):

        if command == IPCCommand.RebuildWindow:
            self.rebuild_window.emit()  # noqa

        elif command == IPCCommand.RefreshUI:
            event = message.get(IPCProp.Event)

            if event == UIRefreshEvent.ActivityLogUpdate:
                self.__update_activity()

            elif event in [UIRefreshEvent.GameConfigChange, UIRefreshEvent.CloudSaveFilesChange]:
                self.__update_games_configuration(event)

            _logger.debug("Refreshing UI with %s event.", event)
            self.refresh_ui.emit(event)  # noqa

    def notify_children(self, message: dict):
        """
        Used to send message to all child processes
        that are running in background.
        """

        _logger.debug("Sending message to child processes.")

        for process in self.__child_processes:
            process.send(message)
            _logger.debug("Sent message to socket on port %d", process.port)

    @staticmethod
    def __update_activity():
        add_dynamic_data(
            HolderObject.Activity, 
            GDrive.download_json_file(context().config.activity_log_file_id)
        )
        context().activity.refresh()

    @staticmethod
    def __update_games_configuration(event: str):

        # If game service_info changed on drive then download it again
        # and reinitialize game state.
        if event == UIRefreshEvent.GameConfigChange:
            add_dynamic_data(
                HolderObject.GamesConfig, 
                GDrive.download_json_file(context().config.games_config_file_id)
            )
            context().games.initialize()

        for game in context().games:
            game.meta.local.calculate_checksum()
            game.meta.drive.refresh()

            # When auto mode is enabled, and save was
            # downloaded/uploaded from another service
            # then we need to reload it in
            # main application.
            if game.settings.auto_mode:
                game.meta.local.refresh()


ui_socket = UISocket()
