from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel

from savegem.app.gui.component import CustomComponentMixin


class QCustomLabel(QLabel, CustomComponentMixin):
    """
    Custom QT QLabel widget.
    """

    def set_content(self, content):

        if isinstance(content, QPixmap):
            self.setPixmap(content)
        else:
            self.setText(content)

    def apply_alignment(self):
        self.setAlignment(self.metadata.alignment)
