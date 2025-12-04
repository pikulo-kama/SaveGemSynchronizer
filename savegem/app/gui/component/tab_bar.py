from PyQt6.QtWidgets import QTabBar

from savegem.app.gui.component import CustomComponentMixin


class QCustomTabBar(CustomComponentMixin, QTabBar):
    """
    Custom QTabBar widget.
    """

    def __init__(self, *args, **kw):
        QTabBar.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
