from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, pyqtProperty
from PyQt6.QtWidgets import QDialog

from savegem.app.gui.component import CustomComponentMixin


class QCustomDialog(QDialog, CustomComponentMixin):
    """
    Custom dialog component.
    Has sliding animation and allows
    to dismiss dialog on timer.
    """

    def __init__(self):
        QDialog.__init__(self)
        CustomComponentMixin.__init__(self)

        self.__top_offset = 0
        self.__slide_duration = 250
        self.__show_duration = 3000

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Popup
        )

        self.setModal(True)

        self.__animation = QPropertyAnimation(self, b"geometry")
        self.__animation.setDuration(self.__slide_duration)  # milliseconds
        self.__animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.__hide_timer = QTimer(self)
        self.__hide_timer.setSingleShot(True)
        self.__hide_timer.timeout.connect(self.__animate_hide)  # noqa

    @pyqtProperty(int)
    def top_offset(self):
        """
        Top offset.
        Padding between top of the application
        window and top of dialog (px).
        """
        return self.__top_offset

    @top_offset.setter
    def top_offset(self, offset):
        """
        Used to set top offset.
        """
        self.__top_offset = offset

    @pyqtProperty(int)
    def slide_duration(self):
        """
        Slide duration.
        Amount of time sliding animation will
        take (ms).
        """
        return self.__slide_duration

    @slide_duration.setter
    def slide_duration(self, duration):
        """
        Used to set slide duration.
        """

        self.__animation.setDuration(duration)
        self.__slide_duration = duration

    @pyqtProperty(int)
    def show_duration(self):
        """
        Show duration.
        Represents amount of time popup will
        be visible until it would disappear (ms).
        """
        return self.__show_duration

    @show_duration.setter
    def show_duration(self, duration):
        """
        Used to set show duration.
        """
        self.__show_duration = duration

    def exec(self):
        """
        Used to display dialog on top
        of other elements.

        Will show dialog using defined animation.
        """

        self.adjustSize()
        self.__animate_show()

        super().exec()

    def __animate_show(self):
        """
        Used to animate dialog sliding in.
        """

        if not self.parent():
            return

        parent_width = self.parent().rect().width()
        dialog_width = self.width()
        dialog_height = self.height()

        # 1. Calculate the final position (centered horizontally, at the top)
        x = (parent_width - dialog_width) // 2
        y = self.__top_offset
        rect = QRect(x, y, dialog_width, dialog_height)

        # 2. Calculate the start position (hidden just above the top edge)
        start_x = x
        start_y = -dialog_height
        start_rect = QRect(start_x, start_y, dialog_width, dialog_height)

        # Set up and start the animation
        self.__animation.setStartValue(start_rect)
        self.__animation.setEndValue(rect)

        # Show the widget before starting the animation
        self.show()
        self.__animation.start()

        # Start the timer to hide the dialog after the display time
        self.__hide_timer.start(self.__slide_duration + self.__show_duration)

    def __animate_hide(self):
        """
        Used to animate dialog sliding out.
        """

        dialog_height = self.height()
        current_rect = self.geometry()
        end_rect = QRect(current_rect.x(), -dialog_height, current_rect.width(), current_rect.height())

        # Disconnect the current animation's
        # finished signal if it's connected.
        try:
            self.__animation.finished.disconnect()  # noqa
        except TypeError:
            pass

        self.__animation.finished.connect(self.close)  # noqa
        self.__animation.setStartValue(current_rect)
        self.__animation.setEndValue(end_rect)
        self.__animation.start()
