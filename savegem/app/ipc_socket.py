from savegem.common.core import app
from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket, IPCCommand
from savegem.common.util.logger import get_logger
from savegem.common.util.thread import execute_in_thread
from savegem.gdrive_watcher.ipc_socket import google_drive_watcher_socket
from savegem.process_watcher.ipc_socket import process_watcher_socket

_logger = get_logger(__name__)


class _UISocket(IPCSocket):

    def __init__(self):
        super().__init__(prop("ipc.uiSocketPort"))
        self.__child_processes = [google_drive_watcher_socket, process_watcher_socket]

    def _handle(self, command: str, message: dict):

        from savegem.app.gui.window import gui

        if command == IPCCommand.RefreshUI:
            event = message.get("event")

            # When auto mode is enabled, and save was
            # downloaded/uploaded from another service
            # then we need to reload it in
            # main application.
            if app.state.is_auto_mode:
                app.games.reload()

            _logger.debug("Refreshing UI with %s event.", event)
            execute_in_thread(lambda: gui.refresh(event))

    def notify_children(self, message: dict):
        """
        Used to send message to all child processes
        that are running in background.
        """
        for process in self.__child_processes:
            process.send(message)


ui_socket = _UISocket()
