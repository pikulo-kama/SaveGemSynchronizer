from PyQt6.QtCore import Qt, QSize, QRect, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath


def round_image(pixmap: QPixmap, radius: int = None) -> QPixmap:
    """
    Takes a QPixmap and returns a new QPixmap rounded to specified radius.
    If radius is not provided then pixmap would be clipped to circle shape.
    """

    width = pixmap.width()
    height = pixmap.height()
    effective_radius = min(width, height) // 2

    if radius is not None:
        effective_radius = min(effective_radius, radius)

    # Create a new pixmap with an alpha channel
    circular_pixmap = QPixmap(pixmap.size())
    circular_pixmap.fill(Qt.GlobalColor.transparent)

    # Use a QPainter to draw on the new pixmap
    painter = QPainter(circular_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Create a circular path
    path = QPainterPath()
    rectangle = QRect(0, 0, width, height)
    path.addRoundedRect(QRectF(rectangle), effective_radius, effective_radius)

    # Clip the painter to the circular path
    painter.setClipPath(path)

    # Draw the original pixmap
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return circular_pixmap


def scale_image(pixmap: QPixmap, width: int, height: int = None) -> QPixmap:
    """
    Used to scale image to provided size.
    """

    if height is None:
        height = width

    return pixmap.scaled(
        QSize(width, height),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )
