from kui.core.shortcut import prop
from savegem.common.core.ipc_socket import IPCSocket


process_watcher_socket = IPCSocket(prop("ipc.process-watcher-port"))  # pragma: no cover
