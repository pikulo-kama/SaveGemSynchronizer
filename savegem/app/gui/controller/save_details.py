from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import QAttr
from savegem.app.gui.controller import WidgetController
from savegem.common.core.context import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


_status_type_map = {
    SyncStatus.LocalOnly: "warning",
    SyncStatus.NoInformation: "warning",
    SyncStatus.UpToDate: "success",
    SyncStatus.NeedsDownload: "warning",
    SyncStatus.NeedsUpload: "warning"
}


class SaveStatusController(WidgetController):
    """
    Used to update stylesheet of save status widget
    based on synchronization status of current game.
    """

    def refresh(self, save_status_container: QCustomWidget):
        sync_status = app().games.current.meta.sync_status
        save_status_container.setProperty(QAttr.Id, _status_type_map.get(sync_status))
