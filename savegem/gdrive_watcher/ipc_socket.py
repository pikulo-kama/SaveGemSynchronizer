from kui.core.app import KamaApplication
from savegem.common.core.ipc_socket import IPCSocket


_app = KamaApplication()
google_drive_watcher_socket = IPCSocket(_app.config.get("ipc.google-drive-watcher-port"))  # pragma: no cover
