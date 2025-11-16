from savegem.common.core.holders import prop
from savegem.common.core.ipc_socket import IPCSocket


google_drive_watcher_socket = IPCSocket(prop("ipc.gdriveWatcherSocketPort"))  # pragma: no cover
