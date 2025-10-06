from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class ProcessWatcherSocket(IPCSocket):

    def __init__(self):
        super().__init__(prop("ipc.processWatcherSocketPort"))

    def _handle(self, command: str, message: dict):  # pragma: no cover
        pass


process_watcher_socket = ProcessWatcherSocket()
