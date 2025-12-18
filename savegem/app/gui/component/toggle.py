from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, Qt
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from PyQt6.QtWidgets import QPushButton
from savegem.app.gui.component import CustomComponentMixin
from savegem.app.gui.constants import QBool


class QCustomToggle(CustomComponentMixin, QPushButton):
    """
    A custom animated toggle switch component that extends QPushButton.

    This component provides a modern "switch" visual style with a sliding thumb
    and customizable track/thumb colors. It supports state-based animations and
    is fully compatible with Qt Style Sheets through dynamic properties.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the toggle switch with default dimensions, colors, and
        animation configurations.
        """

        QPushButton.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)

        self.setCheckable(True)
        self.__polishRecursionGuard = False

        self.__width = 60
        self.__height = 30

        self.__track_color = QColor("gray")
        self.__thumb_color = QColor("white")
        self.__border_color = QColor("transparent")

        self.__thumb_offset = 0
        self.__animation = QPropertyAnimation(self, b"thumb_offset", self)
        self.__animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.__animation.setDuration(250)  # milliseconds

        self.clicked.connect(self.__animate_toggle)  # noqa
        self.toggled.connect(self.__on_toggle)   # noqa

    @pyqtProperty(int)
    def thumb_offset(self):
        """
        Retrieves the current horizontal offset of the thumb.
        """
        return self.__thumb_offset

    @thumb_offset.setter
    def thumb_offset(self, offset):
        """
        Sets the horizontal offset of the thumb and triggers a repaint.

        Args:
            offset (int): The pixel offset from the left edge.
        """

        self.__thumb_offset = offset
        self.update()

    @pyqtProperty(QColor)
    def track_color(self):
        """
        Retrieves the current color of the toggle's background track.
        """
        return self.__track_color

    @track_color.setter
    def track_color(self, color: QColor):
        """
        Sets the color of the toggle's background track and triggers a repaint.

        Args:
            color (QColor): The color to apply to the track.
        """

        self.__track_color = color
        self.update()

    @pyqtProperty(QColor)
    def thumb_color(self):
        """
        Retrieves the current color of the sliding thumb.
        """
        return self.__thumb_color

    @thumb_color.setter
    def thumb_color(self, color: QColor):
        """
        Sets the color of the sliding thumb and triggers a repaint.

        Args:
            color (QColor): The color to apply to the thumb.
        """

        self.__thumb_color = color
        self.update()

    @pyqtProperty(QColor)
    def border_color(self):
        """
        Retrieves the current border color of the toggle track.
        """
        return self.__border_color

    @border_color.setter
    def border_color(self, color: QColor):
        """
        Sets the border color of the toggle track and triggers a repaint.

        Args:
            color (QColor): The color to apply to the track border.
        """

        self.__border_color = color
        self.update()

    def setChecked(self, checked):
        """
        Manually sets the checked state of the toggle and triggers
        the associated animations.

        Args:
            checked (bool): The desired checked state.
        """

        super().setChecked(checked)
        self.__animate_toggle()
        self.__on_toggle(checked)

    def setFixedWidth(self, width):
        """
        Sets a fixed width for the toggle and updates internal dimension tracking.

        Args:
            width (int): Width in pixels.
        """

        self.__width = width
        super().setFixedWidth(width)

    def setFixedHeight(self, height):
        """
        Sets a fixed height for the toggle and updates internal dimension tracking.

        Args:
            height (int): Height in pixels.
        """

        self.__height = height
        super().setFixedHeight(height)

    def paintEvent(self, event):
        """
        Renders the toggle switch components using QPainter.

        Draws the rounded rectangular track and the circular thumb based on
        the current thumb_offset and color properties.

        Args:
            event (QPaintEvent): The paint event provided by Qt.
        """

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        radius = self.__height / 2

        # Draw track
        painter.setBrush(QBrush(self.__track_color))
        painter.setPen(QPen(self.__border_color, 1))
        painter.drawRoundedRect(0, 0, self.__width, self.__height, radius, radius)

        # Draw thumb
        thumb_size = self.__height - 4  # slightly smaller than track height
        thumb_rect = QRect(self.__thumb_offset + 2, 2, thumb_size, thumb_size)
        painter.setBrush(QBrush(self.__thumb_color))
        # No border for thumb
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(thumb_rect)

    def __animate_toggle(self):
        """
        Calculates the target position and starts the thumb sliding animation.
        """

        end_value = self.__width - self.__height if self.isChecked() else 0

        self.__animation.setStartValue(self.__thumb_offset)
        self.__animation.setEndValue(end_value)
        self.__animation.start()

    def __on_toggle(self, checked):
        """
        Updates dynamic properties and refreshes styles when the state is toggled.

        Args:
            checked (bool): The new checked state.
        """

        self.setProperty("checked", QBool(checked))
        self.__polish()
        self.update()

    def __polish(self):
        """
        Forces a re-evaluation of the widget's style to apply QSS changes
        linked to dynamic properties.
        """

        if not self.__polishRecursionGuard:
            self._polishRecursionGuard = True
            self.style().unpolish(self)
            self.style().polish(self)
            self._polishRecursionGuard = False
