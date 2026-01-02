from kui.core.shortcut import prop
from savegem.common.core.ipc_socket import IPCSocket


google_drive_watcher_socket = IPCSocket(prop("ipc.google-drive-watcher-port"))  # pragma: no cover
