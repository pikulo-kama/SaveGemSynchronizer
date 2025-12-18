from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy

from savegem.app.gui.component import CustomComponentMixin


class QCustomLabel(CustomComponentMixin, QLabel):
    """
    Custom QT QLabel widget extended with CustomComponentMixin.

    This base class handles standard text and pixmap content resolution,
    ensuring consistent behavior across all label-based components in the application.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the label with plain text format by default and sets up the mixin.
        """

        QLabel.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
        self.setTextFormat(Qt.TextFormat.PlainText)

    def set_content(self, content):
        """
        Applies either a QPixmap or a string to the label based on the input type.

        Args:
            content (Union[QPixmap, str]): The resolved content to display.
        """

        if isinstance(content, QPixmap):
            self.setPixmap(content)
        else:
            self.setText(content)

    def apply_alignment(self):
        """
        Applies the text alignment specified in the widget's metadata.
        """
        self.setAlignment(self.metadata.alignment)


class QWordWrapLabel(QCustomLabel):
    """
    A specialized label that automatically wraps text to the next line.

    Useful for descriptions or long strings where the content must fit within
    the horizontal bounds of the parent container.
    """

    def __init__(self, *args, **kw):
        """
        Configures the label for word wrapping and sets an expanding size policy.
        """

        super().__init__(*args, **kw)
        self.setWordWrap(True)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )


class QRichLabel(QCustomLabel):
    """
    A label component configured to render HTML-based rich text.

    Automatically handles hyperlinks by opening them in the system's
    default web browser.
    """

    def __init__(self, *args, **kw):
        """
        Sets the text format to RichText and enables external link interaction.
        """

        super().__init__(*args, **kw)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setOpenExternalLinks(True)
