from PyQt6.QtGui import QPixmap

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.file import resolve_resource
from savegem.common.util.graphics import scale_image, round_image
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class PixmapResolver(ContentResolver):
    """
    A specialized ContentResolver for handling image assets and QPixmap
    transformations.

    This resolver identifies file paths and applies graphical processing such
    as scaling and rounding based on token parameters like 'scale', 'radius',
    or the 'circle' flag.
    """

    def resolve(self, file_path: str, *args, **kw):
        """
        Resolves the resource path and applies the requested graphical
        transformations to the resulting QPixmap.

        Args:
            file_path (str): The logical path to the image resource.
            *args: Positional arguments (e.g., 'circle' for circular masking).
            **kw: Keyword arguments for 'scale' (int) and 'radius' (int).

        Returns:
            QPixmap: The processed image or an empty pixmap if the path is invalid.
        """

        if file_path is None:
            _logger.error("File path is not valid. Resolving to empty pixmap.")
            return QPixmap()

        file_path = resolve_resource(file_path)
        scale = kw.get("scale")
        radius = kw.get("radius")
        make_circular = "circle" in args

        pixmap = QPixmap(file_path)
        _logger.debug("Creating pixmap for %s", file_path)

        if scale is not None:
            _logger.debug("Scaling image to %s", scale)
            pixmap = scale_image(pixmap, scale)

        if make_circular:
            _logger.debug("Applying circle mask to pixmap.")
            pixmap = round_image(pixmap)

        elif radius is not None:
            _logger.debug("Applying rounded mask to pixmap with radius %d", radius)
            pixmap = round_image(pixmap, radius)

        return pixmap
