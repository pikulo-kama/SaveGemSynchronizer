from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from savegem.app.gui.constants import QObjectName


class QIconTooltip(QLabel):
    """
    Wrapper component that should be used
    to display tooltip messages.
    """

    def __init__(self):
        super().__init__()

        super().setText("!")
        self.setObjectName(QObjectName.InformationIcon)

        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setText(self, text):
        self.setToolTip(text)
