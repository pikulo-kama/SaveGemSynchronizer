import os
import sys
import threading

from PyQt6.QtWidgets import QApplication

from constants import Directory
from savegem.app.gui.window import gui
from savegem.app.ipc_socket import ui_socket
from savegem.app.startup import StartupJob
from savegem.common.core.flag import flags
from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.core.text_resource import TextResource
from savegem.common.util.file import cleanup_directory
from savegem.common.util.logger import get_logger
from savegem.common.core.context import app

_logger = get_logger("app")


def main():
    """
    Application entry point.
    """

    _logger.info("Starting SaveGem application.")
    _logger.info("version %s", prop("version"))

    gui().application = QApplication(sys.argv)

    app().state.on_change(lambda: ui_socket.notify_children(IPCCommand.StateChanged))
    gui().after_init.connect(lambda: flags().gui_initialized.enable())
    gui().after_init.connect(lambda: StartupJob().start())
    gui().before_destroy.connect(teardown)

    gui().show_wait_screen()
    gui().build()

    sys.exit(gui().application.exec())


def teardown():
    """
    Used to clean up temporary data.
    """

    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(Directory().Output)
    _logger.info("Creating directory for dynamic resources.")
    os.mkdir(Directory().TempResources)

    flags().gui_initialized.disable()


def rebuild():
    """
    Used to rebuild window.
    Needed mainly for development purposes
    when data import service sends event to socket
    after reimporting data.
    """

    app().state.refresh()
    TextResource.reset()
    gui().build()


if __name__ == "__main__":  # pragma: no cover
    # Start UI socket.
    ui_socket.refresh_ui.connect(lambda event: gui().refresh(event))
    ui_socket.rebuild_window.connect(rebuild)
    threading.Thread(target=ui_socket.listen, daemon=True).start()
    main()
