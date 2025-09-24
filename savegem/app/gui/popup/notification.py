from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from constants import Resource
from savegem.app.gui.constants import QAttr, QObjectName, QKind
from savegem.common.core.text_resource import tr
from savegem.app.gui.popup import Popup


def notification(message: str):
    """
    Used to display notification message.
    """
    Notification().show_dialog(message)


class Notification(Popup):
    """
    Popup used to display notification messages.
    """

    def __init__(self):
        super().__init__("popup_NotificationTitle", Resource.NotificationIco)

    def _add_controls(self):
        close_button = QPushButton(tr("popup_NotificationButtonClose"))
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setObjectName(QObjectName.Button)
        close_button.setProperty(QAttr.Kind, QKind.Primary)

        close_button.clicked.connect(self.accept)  # noqa

        self._container.addWidget(close_button)
