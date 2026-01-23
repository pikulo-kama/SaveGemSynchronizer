import sys
import threading

from kui.core.app import KamaApplication
from kui.core.shortcut import prop
from kutil.logger import get_logger

from src.savegem.constants import UISection

from src.savegem.app.ipc_socket import ui_socket
from src.savegem.common.core.flag import flags
from src.savegem.common.core.ipc_socket import IPCCommand
from src.savegem.common.service.gdrive import GoogleAuth
from src.savegem.common.core.context import context


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
    application.window.before_destroy.connect(lambda: flags().gui_initialized.disable())

    GoogleAuth.authenticate()
    sys.exit(application.exec())


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
