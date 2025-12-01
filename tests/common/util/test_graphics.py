import pytest
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication


class TestGraphicsUtil:

    @staticmethod
    def create_solid_pixmap(width: int, height: int, color: QColor) -> QPixmap:
        """
        Creates a test QPixmap filled with a single color.
        """

        pixmap = QPixmap(width, height)
        pixmap.fill(color)

        return pixmap


    @pytest.fixture
    def _qt_app(self):
        """
        Ensures a QApplication instance exists for all tests involving Qt objects.
        """

        app = QApplication.instance()

        if app is None:
            app = QApplication([])

        yield app


    def test_square_input_size_and_alpha(self, _qt_app):
        """
        Checks size and alpha channel creation for a standard square pixmap.
        """

        from savegem.common.util.graphics import round_image

        size = 100
        original = self.create_solid_pixmap(size, size, QColor(Qt.GlobalColor.blue))
        circular = round_image(original)

        assert circular.size() == QSize(size, size)
        assert circular.hasAlphaChannel() is True
        assert circular.isNull() is False


    def test_should_round_image_with_radius(self, _qt_app, module_patch, painter_mock):

        from savegem.common.util.graphics import round_image

        size, radius = 100, 10
        original = self.create_solid_pixmap(size, size, QColor(Qt.GlobalColor.blue))

        painter_path_mock = module_patch("QPainterPath")
        round_image(original, radius)

        effective_radius = painter_path_mock.return_value.addRoundedRect.call_args[0][1]
        assert effective_radius == radius


    def test_rectangular_input_size(self, _qt_app):
        """
        Checks size for a rectangular input, which should result in an ellipse clipping.
        """

        from savegem.common.util.graphics import round_image

        width, height = 150, 80
        original = self.create_solid_pixmap(width, height, QColor(Qt.GlobalColor.green))
        circular = round_image(original)

        assert circular.size() == QSize(width, height)


    def test_empty_pixmap(self, _qt_app):
        """
        Checks behavior with a zero-dimension pixmap.
        """

        from savegem.common.util.graphics import round_image

        original = QPixmap(0, 0)
        circular = round_image(original)

        assert original.isNull() is True
        assert circular.isNull() is True


    def test_transparency_at_corners(self, _qt_app):
        """
        Validates that the output pixmap is transparent outside the clipped area
        by checking a corner pixel (which is definitely outside the circle).
        """

        from savegem.common.util.graphics import round_image

        size = 100
        original = self.create_solid_pixmap(size, size, QColor(Qt.GlobalColor.white))
        circular = round_image(original)

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


    def test_input_with_alpha_channel(self, _qt_app):
        """
        Ensures the function handles an input pixmap that already has an alpha channel
        and doesn't unintentionally remove resolver.
        """

        from savegem.common.util.graphics import round_image

        size = 100
        original = QPixmap(size, size)
        original.fill(Qt.GlobalColor.transparent)  # Start transparent

        # Draw a semi-transparent red square in the center
        painter = QPainter(original)
        painter.setBrush(QColor(255, 0, 0, 128))  # Semi-transparent red
        painter.drawRect(25, 25, 50, 50)
        painter.end()

        circular = round_image(original)

        image = circular.toImage()
        center_color = image.pixelColor(50, 50)

        # The center should still be semi-transparent red (alpha=128)
        assert center_color.alpha() == 128
        assert center_color.red() == 255

        # The corner should still be fully transparent (0)
        corner_color = image.pixelColor(1, 1)
        assert corner_color.alpha() == 0


    def test_should_scale_image(self, _qt_app):

        from savegem.common.util.graphics import scale_image

        size = 100
        target_width = 20
        target_height = 30

        original = self.create_solid_pixmap(size, size, QColor(Qt.GlobalColor.white))

        scaled = scale_image(original, target_width, target_height)

        # Should scale to the lower value.
        assert scaled.width() == target_width
        assert scaled.height() == target_width


    def test_should_scale_image_width_only(self, _qt_app):

        from savegem.common.util.graphics import scale_image

        size, target_size = 100, 50
        original = self.create_solid_pixmap(size, size, QColor(Qt.GlobalColor.white))

        scaled = scale_image(original, target_size)

        assert scaled.width() == target_size
        assert scaled.height() == target_size

