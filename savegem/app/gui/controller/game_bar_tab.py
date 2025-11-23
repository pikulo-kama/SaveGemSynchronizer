from PyQt6.QtWidgets import QWidget

from savegem.app.gui.controller import WidgetController
from savegem.app.gui.widget.metadata import UISection


class GameBarTabController(WidgetController):
    """
    Used to rebind tab root widget to home.game_container widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, bar_tab_root: QWidget):
        self._change_widget_parent(bar_tab_root, UISection.HomeSection, "game_container")
