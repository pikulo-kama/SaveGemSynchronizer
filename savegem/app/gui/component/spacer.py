from PyQt6.QtWidgets import QWidget, QSizePolicy

from savegem.app.gui.component import CustomComponentMixin


class QSpacer(QWidget, CustomComponentMixin):
    """
    Simple spacer widget.
    Will take all available space while
    maximally shrinking other widgets.
    """

    def __init__(self):
        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
