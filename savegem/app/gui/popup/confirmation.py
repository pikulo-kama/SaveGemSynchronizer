from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QPushButton

from constants import Resource
from savegem.app.gui.constants import QAttr, QObjectName, QKind
from savegem.app.gui.window import gui
from savegem.common.core.text_resource import tr
from savegem.app.gui.popup import Popup


def confirmation(message: str, callback):
    """
    Present popup used to display confirmation messages.
    """

    popup = Confirmation()
    popup.set_confirm_callback(callback)
    popup.show_dialog(message)


class Confirmation(Popup):
    """
    Popup used to display confirmation messages.
    """

    def __init__(self):
        Popup.__init__(self, gui(), "popup_ConfirmationTitle", Resource.ConfirmationIco)
        self.__confirm_callback = None

    def set_confirm_callback(self, callback):
        """
        Used to set callback that would be executed
        when Confirm button is bein clicked.
        """

        self.__confirm_callback = callback

    def _add_controls(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        def confirm_callback():
            self.accept()

            if self.__confirm_callback is not None:
                self.__confirm_callback()

        confirm_button = QPushButton(tr("popup_ConfirmationButtonConfirm"))
        confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_button.setObjectName(QObjectName.Button)
        confirm_button.setProperty(QAttr.Kind, QKind.Primary)

        close_button = QPushButton(tr("popup_ConfirmationButtonClose"))
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setObjectName(QObjectName.Button)
        close_button.setProperty(QAttr.Kind, QKind.Secondary)

        confirm_button.clicked.connect(confirm_callback)  # noqa
        close_button.clicked.connect(self.reject)  # noqa

        button_layout.addWidget(confirm_button)
        button_layout.addWidget(close_button)

        self._container.addLayout(button_layout)
