from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component import CustomComponentMixin


class QBaseDivider(CustomComponentMixin, QWidget):
    """
    Abstract base class for custom content dividers that integrate with
    PyQt6 stylesheets and the CustomComponentMixin.
    """

    def __init__(self):
        """
        Initializes the base divider with a default line thickness.
        """

        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        self._line_thickness = 1

    def _paint_divider(self, painter: QPainter):  # pragma: no cover
        """
        Internal drawing logic to be implemented by horizontal or vertical
        subclasses.

        Args:
            painter (QPainter): The painter instance used to render the divider.
        """
        pass

    def paintEvent(self, event):
        """
        Handles the widget's paint request by retrieving the background color
        from the current palette and delegating the draw call.

        Args:
            event (QPaintEvent): The paint event provided by Qt.
        """

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
    A horizontal line widget used to visually separate sections in a
    vertical layout.
    """

    def __init__(self):
        """
        Initializes the horizontal divider with a fixed height
        using configured line thickness.
        """

        QBaseDivider.__init__(self)
        super().setFixedHeight(self._line_thickness)

    def _paint_divider(self, painter: QPainter):
        """
        Calculates the vertical center and draws a horizontal rectangle
        across the width of the widget.

        Args:
            painter (QPainter): The painter instance used for drawing.
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
        Overrides the standard setFixedHeight to protect the default
        divider dimensions.

        Args:
            height (int): The target height (ignored).
        """
        pass


class QVDivider(QBaseDivider):
    """
    A vertical line widget used to visually separate sections in a
    horizontal layout.
    """

    def __init__(self):
        """
        Initializes the vertical divider with a fixed width using
        configured line thickness.
        """

        QBaseDivider.__init__(self)
        super().setFixedWidth(self._line_thickness)

    def _paint_divider(self, painter: QPainter):
        """
        Calculates the horizontal center and draws a vertical rectangle
        across the height of the widget.

        Args:
            painter (QPainter): The painter instance used for drawing.
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
        Overrides the standard setFixedWidth to protect the default
        divider dimensions.

        Args:
            width (int): The target width (ignored).
        """
        pass
