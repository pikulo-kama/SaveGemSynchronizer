from PyQt6.QtGui import QPixmap

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.file import resolve_resource
from savegem.common.util.graphics import scale_image, round_image


class PixmapResolver(ContentResolver):
    """
    Used to resolve image tokens.
    Allow to scale and round image.
    """

    def resolve(self, file_path: str, **kw):

        if file_path is None:
            return QPixmap()

        file_path = resolve_resource(file_path)
        scale = kw.get("scale")
        radius = kw.get("radius")
        make_circular = kw.get("circle")

        pixmap = QPixmap(file_path)

        if scale is not None:
            pixmap = scale_image(pixmap, scale)

        if make_circular:
            pixmap = round_image(pixmap)

        elif radius is not None:
            pixmap = round_image(pixmap, radius)

        return pixmap
