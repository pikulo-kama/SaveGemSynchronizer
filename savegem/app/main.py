# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
from savegem.common import initializer
from savegem.common.cleanup import teardown
import threading

from savegem.app.gui.window import gui
from savegem.app.gui.ipc_socket import ui_socket
from savegem.common.core.ipc_socket import IPCCommand
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

    app.user.initialize(GDrive.get_current_user())
    app.games.download()

    gui.initialize()
    gui.after_init(lambda: google_drive_watcher_socket.send(IPCCommand.GUIInitialized))
    gui.before_destroy(teardown)
    gui.build()

    _logger.info("Application shut down.")


if __name__ == "__main__":
    # Start UI socket.
    threading.Thread(target=ui_socket.listen, daemon=True).start()
    _main()
