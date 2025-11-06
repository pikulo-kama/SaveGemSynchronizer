from savegem.app.gui.component.label import QCustomLabel
from savegem.app.gui.constants import QBool
from savegem.app.gui.controller import WidgetController
from savegem.common.core.context import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class SyncStatusController(WidgetController):
    """
    Used to update stylesheet of sync status badge
    based on synchronization status of current game.
    """

    def refresh(self, sync_status_badge: QCustomLabel):
        sync_status = app().games.current.meta.sync_status

        # Only show badge when sync is not up-to-date with cloud.
        sync_status_badge.setProperty("hidden", QBool(sync_status == SyncStatus.UpToDate))
        sync_status_badge.update_styles()
