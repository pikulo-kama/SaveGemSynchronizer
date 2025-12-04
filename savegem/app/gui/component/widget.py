from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component import CustomComponentMixin


class QCustomWidget(CustomComponentMixin, QWidget):
    """
    Custom QWidget widget.
    """

    def __init__(self, *args, **kw):
        QWidget.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)

        # Required to properly display background-color properties
        # defined in widget style.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
