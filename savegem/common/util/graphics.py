from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import QApplication


def get_color_mode():
    """
    Used to get current color mode.
    """

    mode = "light"
    color_scheme = QApplication.instance().styleHints().colorScheme()  # noqa

    if color_scheme == Qt.ColorScheme.Dark:
        mode = "dark"

    return mode


def make_circular_image(pixmap: QPixmap) -> QPixmap:
    """
    Takes a QPixmap and returns a new QPixmap clipped to a circular shape.
    """

    # Create a new pixmap with an alpha channel
    circular_pixmap = QPixmap(pixmap.size())
    circular_pixmap.fill(Qt.GlobalColor.transparent)

    # Use a QPainter to draw on the new pixmap
    painter = QPainter(circular_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Create a circular path
    path = QPainterPath()
    path.addEllipse(0, 0, pixmap.width(), pixmap.height())

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
