from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from savegem.common.util.file import resolve_resource


class QIconTooltip(QLabel):
    """
    Wrapper component that should be used
    to display tooltip messages.
    """

    def __init__(self):
        super().__init__()

        self.setPixmap(QPixmap(resolve_resource("tooltip.svg")))

        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setText(self, text):
        self.setToolTip(text)
