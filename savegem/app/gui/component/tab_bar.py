from PyQt6.QtWidgets import QTabBar

from savegem.app.gui.component import CustomComponentMixin


class QCustomTabBar(CustomComponentMixin, QTabBar):
    """
    Custom QTabBar component that extends the standard PyQt6 QTabBar with
    CustomComponentMixin functionality.

    This class serves as the navigation header for tabbed layouts, allowing for
    customized metadata-driven behavior and styling consistent with other
    SaveGem components.
    """

    def __init__(self, *args, **kw):
        """
        Initializes the tab bar and the component mixin.
        """

        QTabBar.__init__(self, *args, **kw)
        CustomComponentMixin.__init__(self)
