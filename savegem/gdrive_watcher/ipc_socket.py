from constants import File
from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket, IPCCommand
from savegem.common.util.file import save_file, resolve_temp_file
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class GdriveWatcherSocket(IPCSocket):

    def __init__(self):
        super().__init__(prop("ipc.gdriveWatcherSocketPort"))

    def _handle(self, command: str, message: dict):

        if command == IPCCommand.GUIInitialized:
            _logger.debug("Received GUI Initialized command.")
            save_file(resolve_temp_file(File.GUIInitializedFlag), "")


google_drive_watcher_socket = GdriveWatcherSocket()
