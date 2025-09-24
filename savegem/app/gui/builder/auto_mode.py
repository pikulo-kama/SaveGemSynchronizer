from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

from savegem.app.gui.constants import QAttr, QKind, QObjectName
from savegem.app.gui.popup.notification import notification
from savegem.common.core import app
from savegem.app.gui.window import _GUI
from savegem.app.gui.builder import UIBuilder
from savegem.common.core.text_resource import tr
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class AutoModeBuilder(UIBuilder):
    """
    Used to build button to enable auto download/upload mode.
    Always enabled.
    """

    def __init__(self):
        super().__init__()
        self.__auto_mode_button: QPushButton

    def build(self, gui: _GUI):
        self.__add_auto_mode_button(gui)

    def refresh(self, gui: _GUI):

        button_kind = QKind.Secondary

        if not app.state.is_auto_mode:
            button_kind = QKind.Disabled

        self.__auto_mode_button.setProperty(QAttr.Kind, button_kind)
        self.__auto_mode_button.style().polish(self.__auto_mode_button)

        _logger.debug(
            "Auto mode updated, current state = %s",
            "ON" if app.state.is_auto_mode else "OFF"
        )

    def __add_auto_mode_button(self, gui: _GUI):
        """
        Used to render auto upload/download button.
        """

        def callback():
            # Toggle state of button
            if app.state.is_auto_mode:
                app.state.is_auto_mode = False
                message = tr("notification_AutoModeOff")

            else:
                app.state.is_auto_mode = True
                message = tr("notification_AutoModeOn")

            # No need to fully reload the UI since no other visual components
            # would be affected.
            self.refresh(gui)
            notification(message)

        self.__auto_mode_button = QPushButton("A")
        self.__auto_mode_button.clicked.connect(callback)  # noqa
        self.__auto_mode_button.setObjectName(QObjectName.SquareButton)

        self._add_interactable(self.__auto_mode_button)

        gui.top_left.layout().addWidget(
            self.__auto_mode_button, 0, 0,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
