from PyQt6.QtGui import QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QPushButton

from savegem.app.gui.constants import QAttr, QBool


class QCustomPushButton(QPushButton):
    """
    Custom button component.
    Replaces default 'disable' behavior.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.__is_enabled = True
        self.setProperty(QAttr.Disabled, QBool(False))

    def setEnabled(self, is_enabled):
        self.__is_enabled = is_enabled
        self.setProperty(QAttr.Disabled, QBool(not is_enabled))
        self.style().polish(self)

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
