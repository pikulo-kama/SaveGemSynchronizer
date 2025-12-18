from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, pyqtProperty
from PyQt6.QtWidgets import QDialog

from savegem.app.gui.component import CustomComponentMixin


class QCustomDialog(CustomComponentMixin, QDialog):
    """
    Custom dialog component that supports sliding animations and timed dismissal.

    This dialog is frameless and modal by default, designed to slide in from the
    top of its parent window and automatically hide itself after a specified
    duration if configured.
    """

    def __init__(self):
        """
        Initializes the dialog with default animation settings and window flags.
        """

        QDialog.__init__(self)
        CustomComponentMixin.__init__(self)

        self.__top_offset = 0
        self.__slide_duration = 250
        self.__show_duration = 0

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
        self.__hide_timer.timeout.connect(self.hide)  # noqa

    @pyqtProperty(int)
    def top_offset(self):
        """
        Returns the top offset padding between the application window and the dialog.
        """
        return self.__top_offset

    @top_offset.setter
    def top_offset(self, offset: int):
        """
        Sets the vertical padding for the dialog's final position.

        Args:
            offset (int): Padding in pixels.
        """
        self.__top_offset = offset

    @pyqtProperty(int)
    def slide_duration(self):
        """
        Returns the duration of the sliding animation in milliseconds.
        """
        return self.__slide_duration

    @slide_duration.setter
    def slide_duration(self, duration):
        """
        Updates the animation duration and the internal duration state.

        Args:
            duration (int): Animation time in milliseconds.
        """

        self.__animation.setDuration(duration)
        self.__slide_duration = duration

    @pyqtProperty(int)
    def show_duration(self):
        """
        Returns the amount of time the popup remains visible before auto-dismissing.
        """
        return self.__show_duration

    @show_duration.setter
    def show_duration(self, duration):
        """
        Sets the visibility duration. A value of 0 or less prevents auto-dismissal.

        Args:
            duration (int): Visibility time in milliseconds.
        """
        self.__show_duration = duration

    def exec(self):
        """
        Displays the dialog modally with the entry animation.
        """

        self.adjustSize()
        self.show()

        super().exec()

    def show(self):
        """
        Calculates positioning and triggers the slide-in animation from the top.
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
        super().show()
        self.__animation.start()

        # Start the timer to hide the dialog after the display time.
        # Only do this if show duration is positive value.
        if self.__show_duration > 0:
            self.__hide_timer.start(self.__slide_duration + self.__show_duration)

    def hide(self):
        """
        Triggers the slide-out animation and closes the dialog upon completion.
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
