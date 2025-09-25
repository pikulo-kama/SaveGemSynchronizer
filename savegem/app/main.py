import sys
import threading

from PyQt6.QtWidgets import QApplication

from constants import Directory
from savegem.app.gui.style import load_stylesheet
from savegem.app.gui.window import gui
from savegem.app.ipc_socket import ui_socket
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.util.file import cleanup_directory
from savegem.common.util.logger import get_logger
from savegem.common.service.gdrive import GDrive
from savegem.common.core import app

_logger = get_logger("app")


def _main():
    """
    Application entry point.
    """

    _logger.info("Initializing application.")

    # Startup initialization.
    app.user.initialize(GDrive.get_current_user)
    app.games.download()
    app.games.current.meta.drive.refresh()
    app.activity.refresh()

    application = QApplication(sys.argv)
    application.setStyleSheet(load_stylesheet())

    app.state.on_change(lambda: ui_socket.notify_children(IPCCommand.StateChanged))
    gui().after_init.connect(lambda: ui_socket.notify_children(IPCCommand.GUIInitialized))
    gui().before_destroy.connect(_teardown)
    gui().build()

    sys.exit(application.exec())


def _teardown():
    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(Directory.Output)


if __name__ == "__main__":
    # Start UI socket.
    threading.Thread(target=ui_socket.listen, daemon=True).start()
    _main()
