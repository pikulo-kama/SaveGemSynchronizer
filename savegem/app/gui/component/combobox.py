from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QComboBox


class QCustomComboBox(QComboBox):
    """
    Custom QT ComboBox component.
    Overwrites default QComboBox
    behaviour by allowing to change
    cursor when widget is disabled.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.__is_enabled = True

    def setEnabled(self, is_enabled):
        self.__is_enabled = is_enabled

    def mousePressEvent(self, event: QMouseEvent):
        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().mousePressEvent(event)
            return

        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        # Only handle events if component
        # enabled.
        if self.__is_enabled:
            super().keyPressEvent(event)
            return

        event.accept()
