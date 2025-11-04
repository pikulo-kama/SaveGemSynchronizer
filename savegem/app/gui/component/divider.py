from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QFrame, QWidget

from savegem.app.gui.component import CustomComponentMixin


class QHDivider(QWidget, CustomComponentMixin):
    """
    Simple horizontal divider widget.
    """

    def __init__(self):
        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        self.__line_thickness = 1
        super().setFixedHeight(self.__line_thickness)

    def paintEvent(self, event):
        """
        Draws the horizontal divider line using the QSS background-color.
        """

        painter = QPainter(self)

        # 1. Get the color from the current style sheet
        # We use 'background-color' as the QSS property to control the color.
        # This is the standard way to retrieve QSS attributes in the paintEvent.
        color_variant = self.palette().color(self.backgroundRole())
        line_color = QColor(color_variant)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(line_color)

        # 2. Calculate the position for the line
        # Draw a 1-pixel line centered vertically in the available height (20px).
        line_y = (self.height() - self.__line_thickness) // 2

        # 3. Draw the line (rectangle)
        painter.drawRect(
            0,
            line_y,
            self.width(),
            self.__line_thickness
        )

    def setFixedHeight(self, height):
        """
        Prevent setting a custom height if the intent is to maintain the
        default divider spacing of 20px.
        """
        pass


class QVDivider(QFrame, CustomComponentMixin):
    """
    Simple vertical divider widget.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        CustomComponentMixin.__init__(self)

        self.__line_thickness = 1
        super().setFixedWidth(self.__line_thickness)

    def paintEvent(self, event):
        """
        Draws the vertical divider line using the QSS background-color.
        """

        painter = QPainter(self)

        # 1. Get the color from the current style sheet (uses background-color)
        color_variant = self.palette().color(self.backgroundRole())
        line_color = QColor(color_variant)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(line_color)

        # 2. Calculate the position for the line
        # Draw a 1-pixel line centered horizontally in the available width (20px).
        line_x = (self.width() - self.__line_thickness) // 2

        # 3. Draw the line (rectangle)
        # The line goes from the top (0) to the bottom (self.height())
        painter.drawRect(
            line_x,
            0,
            self.__line_thickness,
            self.height()
        )

    def setFixedWidth(self, width):
        """
        Prevent setting a custom width if the intent is to maintain the
        default divider spacing of 20px.
        """
        pass
