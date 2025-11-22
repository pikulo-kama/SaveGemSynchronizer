from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy

from savegem.app.gui.component import CustomComponentMixin


class QCustomLabel(QLabel, CustomComponentMixin):
    """
    Custom QT QLabel widget.
    """

    def __init__(self, *args, **kw):
        QLabel.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
        self.setTextFormat(Qt.TextFormat.PlainText)

    def set_content(self, content):

        if isinstance(content, QPixmap):
            self.setPixmap(content)
        else:
            self.setText(content)

    def apply_alignment(self):
        self.setAlignment(self.metadata.alignment)


class QWordWrapLabel(QCustomLabel):
    """
    Custom Qt QLabel widget.
    Word wraps if content length exceeds geometry
    of parent widget.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setWordWrap(True)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )


class QRichLabel(QCustomLabel):
    """
    Custom QT QLabel widget.
    Handles hyperlinks and other rich text.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setOpenExternalLinks(True)
