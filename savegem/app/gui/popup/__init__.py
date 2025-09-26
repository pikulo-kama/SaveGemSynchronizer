from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

from savegem.common.core.text_resource import tr
from savegem.common.core.holders import prop
from savegem.app.gui.window import gui
from savegem.common.util.file import resolve_resource
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class Popup(QDialog):
    """
    General popup window component.
    """

    def __init__(self, title_text_resource, icon):
        super().__init__(gui())

        _logger.info("Initializing popup.")
        _logger.debug("popupTitle = %s", title_text_resource)

        self.setWindowTitle(tr(title_text_resource))
        self.setWindowIcon(QIcon(resolve_resource(icon)))
        self.setFixedSize(prop("popupWidth"), prop("popupHeight"))
        self.setModal(True)

        self._container = QVBoxLayout(self)
        self.adjustSize()

    def show_dialog(self, message):
        """
        Used to display popup with provided message.
        """

        _logger.debug("popupMessage = %s", message)

        message_label = QLabel(message)
        message_label.setObjectName("popupTitle")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._container.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._add_controls()

        self.exec()

    def showEvent(self, event):
        # Will center popup
        # in top-center position
        # when it's being rendered.
        parent = self.parent().geometry()
        x = parent.x() + (parent.width() - self.width()) // 2

        self.move(x, parent.y())
        super().showEvent(event)

    def _add_controls(self):
        """
        Should be overridden in child classes.
        Should be used to add additional or customize existing
        controls in popup.
        """
        pass
