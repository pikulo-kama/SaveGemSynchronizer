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
    A specialized ContentResolver for handling icon resources.

    This resolver transforms file paths into QIconWrapper objects, allowing for
    dynamic scaling via 'size', 'width', or 'height' parameters defined in
    the token.
    """

    DefaultSize: Final[int] = 10

    def resolve(self, file_path: str, *args, **kw):
        """
        Resolves the icon resource path and constructs a scaled icon wrapper.

        Args:
            file_path (str): The logical path to the icon file.
            *args: Unused positional arguments.
            **kw: Keyword arguments for 'size', 'width', or 'height'.

        Returns:
            QIconWrapper: A wrapper around the QIcon with specified dimensions,
                          or None if the path is invalid.
        """

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
