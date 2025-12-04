from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component import CustomComponentMixin


class QBaseDivider(CustomComponentMixin, QWidget):
    """
    Base class for content divider.
    """

    def __init__(self):
        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        self._line_thickness = 1

    def _paint_divider(self, painter: QPainter):  # pragma: no cover
        """
        Used to draw actual divider (rectangle) using provided
        painter instance.
        """
        pass

    def paintEvent(self, event):

        painter = QPainter(self)

        # 1. Get the color from the current style sheet
        # We use 'background-color' as the QSS property to control the color.
        # This is the standard way to retrieve QSS attributes in the paintEvent.
        color_variant = self.palette().color(self.backgroundRole())
        line_color = QColor(color_variant)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(line_color)

        self._paint_divider(painter)


class QHDivider(QBaseDivider):
    """
    Simple horizontal divider widget.
    """

    def __init__(self):
        QBaseDivider.__init__(self)
        super().setFixedHeight(self._line_thickness)

    def _paint_divider(self, painter: QPainter):
        """
        Draws the horizontal divider line using the QSS background-color.
        """

        line_y = (self.height() - self._line_thickness) // 2

        painter.drawRect(
            0,
            line_y,
            self.width(),
            self._line_thickness
        )

    def setFixedHeight(self, height):  # pragma: no cover
        """
        Prevent setting a custom height if the intent is to maintain the
        default divider spacing of 20px.
        """
        pass


class QVDivider(QBaseDivider):
    """
    Simple vertical divider widget.
    """

    def __init__(self):
        QBaseDivider.__init__(self)
        super().setFixedWidth(self._line_thickness)

    def _paint_divider(self, painter: QPainter):
        """
        Draws the vertical divider line using the QSS background-color.
        """

        line_x = (self.width() - self._line_thickness) // 2

        painter.drawRect(
            line_x,
            0,
            self._line_thickness,
            self.height()
        )

    def setFixedWidth(self, width):  # pragma: no cover
        """
        Prevent setting a custom width if the intent is to maintain the
        default divider spacing of 20px.
        """
        pass
