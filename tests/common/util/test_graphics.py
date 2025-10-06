import pytest
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication

from savegem.common.util.graphics import make_circular_image


def create_solid_pixmap(width: int, height: int, color=Qt.GlobalColor.red) -> QPixmap:
    """
    Creates a test QPixmap filled with a single color.
    """

    pixmap = QPixmap(width, height)
    pixmap.fill(color)

    return pixmap


@pytest.fixture
def _qt_app():
    """
    Ensures a QApplication instance exists for all tests involving Qt objects.
    """

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app


def test_square_input_size_and_alpha(_qt_app):
    """
    Checks size and alpha channel creation for a standard square pixmap.
    """

    size = 100
    original = create_solid_pixmap(size, size, Qt.GlobalColor.blue)
    circular = make_circular_image(original)

    assert circular.size() == QSize(size, size)
    assert circular.hasAlphaChannel() is True
    assert circular.isNull() is False


def test_rectangular_input_size(_qt_app):
    """
    Checks size for a rectangular input, which should result in an ellipse clipping.
    """

    width, height = 150, 80
    original = create_solid_pixmap(width, height, Qt.GlobalColor.green)
    circular = make_circular_image(original)

    assert circular.size() == QSize(width, height)


def test_empty_pixmap(_qt_app):
    """
    Checks behavior with a zero-dimension pixmap.
    """

    original = QPixmap(0, 0)
    circular = make_circular_image(original)

    assert original.isNull() is True
    assert circular.isNull() is True


def test_transparency_at_corners(_qt_app):
    """
    Validates that the output pixmap is transparent outside the clipped area
    by checking a corner pixel (which is definitely outside the circle).
    """

    size = 100
    original = create_solid_pixmap(size, size, Qt.GlobalColor.white)
    circular = make_circular_image(original)

    # Convert to QImage to check pixel data
    image = circular.toImage()

    # Check a pixel that should be **inside** (center)
    center_color = image.pixelColor(size // 2, size // 2)
    assert center_color.alpha() == 255  # Should be opaque (from the input)

    # Check a pixel that should be **outside** (corner, e.g., (1, 1))
    corner_color = image.pixelColor(1, 1)
    assert corner_color.alpha() == 0  # Should be fully transparent (clipped)

    # Check an opaque pixel near the edge (e.g., (50, 1))
    # This point is on the top edge, *inside* the circle's vertical extent
    edge_inside_color = image.pixelColor(size // 2, 1)
    assert edge_inside_color.alpha() > 0  # Should be at least partially opaque


def test_input_with_alpha_channel(_qt_app):
    """
    Ensures the function handles an input pixmap that already has an alpha channel
    and doesn't unintentionally remove content.
    """

    size = 100
    original = QPixmap(size, size)
    original.fill(Qt.GlobalColor.transparent)  # Start transparent

    # Draw a semi-transparent red square in the center
    painter = QPainter(original)
    painter.setBrush(QColor(255, 0, 0, 128))  # Semi-transparent red
    painter.drawRect(25, 25, 50, 50)
    painter.end()

    circular = make_circular_image(original)

    image = circular.toImage()
    center_color = image.pixelColor(50, 50)

    # The center should still be semi-transparent red (alpha=128)
    assert center_color.alpha() == 128
    assert center_color.red() == 255

    # The corner should still be fully transparent (0)
    corner_color = image.pixelColor(1, 1)
    assert corner_color.alpha() == 0
