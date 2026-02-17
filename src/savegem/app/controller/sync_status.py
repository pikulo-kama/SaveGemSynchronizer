from typing import Final

from kui.component.label import KamaLabel
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

    Visible: Final[str] = "visible"

    def refresh(self, sync_status_chip: KamaLabel, args: ControllerArgs):
        sync_status = context().games.current.meta.sync_status
        _logger.debug("game=%s, sync_status=%s", context().games.current.name, sync_status.name)

        # Only show badge when sync is not up-to-date with cloud.
        if sync_status != SyncStatus.UpToDate:
            sync_status_chip.add_class(self.Visible)
        else:
            sync_status_chip.remove_class(self.Visible)

        sync_status_chip.update_styles()
