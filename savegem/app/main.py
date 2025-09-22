import threading
import time

from constants import Directory
from savegem.app.gui.window import gui
from savegem.app.ipc_socket import ui_socket
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.util.file import cleanup_directory
from savegem.common.util.logger import get_logger
from savegem.common.service.gdrive import GDrive
from savegem.common.core import app
from savegem.gdrive_watcher.ipc_socket import google_drive_watcher_socket

_logger = get_logger("app")


def _main():
    """
    Application entry point.
    """

    _logger.info("Initializing application.")

    app.state.on_change(lambda: ui_socket.notify_children(IPCCommand.StateChanged))
    app.user.initialize(GDrive.get_current_user)
    app.activity.reload()
    app.games.download()

    gui.initialize()
    gui.after_init(lambda: google_drive_watcher_socket.send(IPCCommand.GUIInitialized))
    gui.before_destroy(_teardown)
    gui.build()

    _logger.info("Application shut down.")


def _teardown():
    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(Directory.Output)


if __name__ == "__main__":
    # Start UI socket.
    threading.Thread(target=ui_socket.listen, daemon=True).start()
    _main()
