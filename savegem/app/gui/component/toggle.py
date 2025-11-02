from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, Qt
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from PyQt6.QtWidgets import QPushButton
from savegem.app.gui.component import CustomComponentMixin
from savegem.app.gui.constants import QBool


class QCustomToggle(QPushButton, CustomComponentMixin):
    """
    Custom toggle button component.
    """

    def __init__(self, *args, **kw):
        QPushButton.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)

        self.setCheckable(True)
        self.__polishRecursionGuard = False

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
        Used to get thumb offset in toggle.
        """
        return self.__thumb_offset

    @thumb_offset.setter
    def thumb_offset(self, offset):
        """
        Used to set thumb offset in toggle.
        """

        self.__thumb_offset = offset
        self.update()

    @pyqtProperty(QColor)
    def track_color(self):
        """
        Used to get track color of toggle.
        """
        return self.__track_color

    @track_color.setter
    def track_color(self, color: QColor):
        """
        Used to set track color of toggle.
        """

        self.__track_color = color
        self.update()

    @pyqtProperty(QColor)
    def thumb_color(self):
        """
        Used to get thumb color of toggle.
        """
        return self.__thumb_color

    @thumb_color.setter
    def thumb_color(self, color: QColor):
        """
        Used to set thumb color of toggle.
        """

        self.__thumb_color = color
        self.update()

    @pyqtProperty(QColor)
    def border_color(self):
        """
        Used to get border color of toggle.
        """
        return self.__border_color

    @border_color.setter
    def border_color(self, color: QColor):
        """
        Used to set border color of toggle.
        """

        self.__border_color = color
        self.update()

    def setChecked(self, checked):
        super().setChecked(checked)
        self.__animate_toggle()
        self.__on_toggle(checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define sizes
        height = self.height()
        width = self.width()
        radius = height / 2

        # Draw track
        painter.setBrush(QBrush(self.__track_color))
        painter.setPen(QPen(self.__border_color, 1))
        painter.drawRoundedRect(0, 0, width, height, radius, radius)

        # Draw thumb
        thumb_size = height - 4  # slightly smaller than track height
        thumb_rect = QRect(self.__thumb_offset + 2, 2, thumb_size, thumb_size)
        painter.setBrush(QBrush(self.__thumb_color))
        painter.setPen(QPen(Qt.PenStyle.NoPen))  # No border for thumb
        painter.drawEllipse(thumb_rect)

    def __animate_toggle(self):
        """
        Toggle animation callback.
        """

        end_value = self.width() - self.height() if self.isChecked() else 0

        self.__animation.setStartValue(self.__thumb_offset)
        self.__animation.setEndValue(end_value)
        self.__animation.start()

    def __on_toggle(self, checked):
        """
        Used to redraw toggle on state change.
        """

        self.setProperty("checked", QBool(checked))
        self.__polish()
        self.update()

    def __polish(self):
        """
        Used to refresh component styles.
        """

        if not self.__polishRecursionGuard:
            self._polishRecursionGuard = True
            self.style().unpolish(self)
            self.style().polish(self)
            self._polishRecursionGuard = False
