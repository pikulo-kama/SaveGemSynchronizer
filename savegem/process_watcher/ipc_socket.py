from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket


process_watcher_socket = IPCSocket(prop("ipc.processWatcherSocketPort"))  # pragma: no cover
