from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtSvg import QSvgRenderer


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


def svg_to_pixmap(raw_svg: str, size: QSize) -> QPixmap:
    """
    Converts an SVG string into a QPixmap.
    """

    svg_data = QByteArray(raw_svg.encode('utf-8'))

    # Create a renderer for the SVG data
    svg_renderer = QSvgRenderer(svg_data)

    # Create a QPixmap to render the SVG onto
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    # Render the SVG onto the pixmap
    painter = QPainter(pixmap)
    svg_renderer.render(painter)
    painter.end()

    return pixmap
