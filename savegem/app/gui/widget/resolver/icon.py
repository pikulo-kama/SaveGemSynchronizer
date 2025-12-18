import dataclasses
from typing import Final

from PyQt6.QtGui import QIcon

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.file import resolve_resource
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


@dataclasses.dataclass
class QIconWrapper:
    """
    A wrapper class that bundles a QIcon with its intended display dimensions.

    This utility is used to ensure icons are rendered or scaled consistently
    across different UI components by storing explicit width and height
    requirements alongside the icon resource.
    """

    icon: QIcon
    """The PyQt icon resource."""

    width: int
    """The target width for the icon in pixels."""

    height: int
    """The target height for the icon in pixels."""


class IconResolver(ContentResolver):
    """
    Used to resolve icon tokens.
    Allow to scale the icon.
    """

    DefaultSize: Final[int] = 10

    def resolve(self, file_path: str, *args, **kw):

        if file_path is None:
            _logger.error("File path is not valid.")
            return None

        file_path = resolve_resource(file_path)
        size = kw.get("size") or self.DefaultSize
        width = kw.get("width") or size
        height = kw.get("height") or size

        icon = QIcon(file_path)
        _logger.debug("Creating icon for %s", file_path)

        return QIconWrapper(icon, width, height)
