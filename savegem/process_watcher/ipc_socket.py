from kui.core.app import KamaApplication
from savegem.common.core.ipc_socket import IPCSocket


_app = KamaApplication()
process_watcher_socket = IPCSocket(_app.config.get("ipc.process-watcher-port"))  # pragma: no cover
