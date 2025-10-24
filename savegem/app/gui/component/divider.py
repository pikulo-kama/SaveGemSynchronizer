from PyQt6.QtWidgets import QFrame

from savegem.app.gui.component import CustomComponentMixin


class QHDivider(QFrame, CustomComponentMixin):
    """
    Simple horizontal divider widget.
    """

    def __init__(self):
        QFrame.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Raised)


class QVDivider(QFrame, CustomComponentMixin):
    """
    Simple vertical divider widget.
    """

    def __init__(self):
        QFrame.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Raised)
