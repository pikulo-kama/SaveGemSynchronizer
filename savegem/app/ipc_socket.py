from PyQt6.QtCore import pyqtSignal, QObject

from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.window import gui
from savegem.common.core.context import app
from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket, IPCCommand, IPCProp
from savegem.common.util.logger import get_logger
from savegem.gdrive_watcher.ipc_socket import google_drive_watcher_socket
from savegem.process_watcher.ipc_socket import process_watcher_socket

_logger = get_logger(__name__)


class UISocket(IPCSocket, QObject):

    refresh_ui = pyqtSignal(str)
    rebuild_window = pyqtSignal()

    def __init__(self):
        IPCSocket.__init__(self, prop("ipc.uiSocketPort"))
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
            gui().mutex.lock()

            try:
                # When auto mode is enabled, and save was
                # downloaded/uploaded from another service
                # then we need to reload it in
                # main application.
                if app().state.is_auto_mode:
                    for game in app().games:
                        game.meta.local.refresh()

                if event == UIRefreshEvent.GameConfigChange:
                    app().games.download()
                    app().games.current.meta.drive.refresh()

                elif event == UIRefreshEvent.ActivityLogUpdate:
                    app().activity.refresh()

                elif event == UIRefreshEvent.CloudSaveFilesChange:
                    app().games.current.meta.drive.refresh()

            finally:
                gui().mutex.unlock()

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


ui_socket = UISocket()
