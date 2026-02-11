from kui.core.app import KamaApplication
from kui.core.shortcut import prop

from savegem.common.core.context import context
from savegem.common.core.ipc_socket import IPCSocket, IPCCommand


class ProcessWatcherSocket(IPCSocket):

    def __init__(self):
        super().__init__(prop("ipc.process-watcher-port"))

    def _handle(self, command: str, message: dict):

        if command == IPCCommand.StateChanged:
            application = KamaApplication()
            context().state.refresh()
            application.translations.locale = context().state.locale


process_watcher_socket = ProcessWatcherSocket()
