from PyQt6.QtGui import QPixmap

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.file import resolve_resource
from savegem.common.util.graphics import scale_image, round_image
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class PixmapResolver(ContentResolver):
    """
    Used to resolve image tokens.
    Allow to scale and round image.
    """

    def resolve(self, file_path: str, *args, **kw):

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
