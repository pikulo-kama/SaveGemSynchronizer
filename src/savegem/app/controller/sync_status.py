from kui.component.label import KamaLabel
from kui.core.constants import KamaAttr, QBool
from kui.core.controller import WidgetController
from kui.core.metadata import ControllerArgs
from kutil.logger import get_logger

from savegem.common.core.context import context
from savegem.common.core.save_meta import SyncStatus

_logger = get_logger(__name__)


class SyncStatusController(WidgetController):
    """
    Used to update stylesheet of sync status badge
    based on synchronization status of current game.
    """

    def refresh(self, sync_status_badge: KamaLabel, args: ControllerArgs):
        sync_status = context().games.current.meta.sync_status
        _logger.debug("game=%s, sync_status=%s", context().games.current.name, sync_status.name)

        # Only show badge when sync is not up-to-date with cloud.
        sync_status_badge.setProperty(KamaAttr.Hidden, QBool(sync_status == SyncStatus.UpToDate))
        sync_status_badge.update_styles()
