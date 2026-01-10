import os
import sys
import threading

from kui.core.app import KamaApplication
from kui.core.shortcut import prop
from kutil.file import cleanup_directory
from kutil.logger import get_logger

from savegem.constants import UISection

from savegem.app.ipc_socket import ui_socket
from savegem.common.core.flag import flags
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.service.gdrive import GoogleAuth
from savegem.common.core.context import context


_logger = get_logger("app")


def main():
    """
    Application entry point.
    """

    application = KamaApplication()

    _logger.info("Starting SaveGem application.")
    _logger.info("version %s", prop("application.version"))

    context().state.on_change(lambda: ui_socket.notify_children(IPCCommand.StateChanged))
    application.window.after_init.connect(lambda: flags().gui_initialized.enable())
    application.window.before_destroy.connect(teardown)

    GoogleAuth.authenticate()
    sys.exit(application.exec())


def teardown():
    """
    Used to clean up temporary data.
    """

    application = KamaApplication()

    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(application.discovery.Output)
    _logger.info("Creating directory for dynamic resources.")
    os.mkdir(application.discovery.TempResources)

    flags().gui_initialized.disable()


def rebuild():
    """
    Used to rebuild window.
    Needed mainly for development purposes
    when data import service sends event to socket
    after reimporting data.
    """

    application = KamaApplication()

    context().state.refresh()
    application.translations.reload()
    application.window.build(UISection.RootSection)


if __name__ == "__main__":  # pragma: no cover

    def on_ui_refresh(event: str):
        application = KamaApplication()
        application.window.refresh(event)

    ui_socket.refresh_ui.connect(on_ui_refresh)
    ui_socket.rebuild_window.connect(rebuild)

    # Start UI socket.
    threading.Thread(target=ui_socket.listen, daemon=True).start()
    main()
