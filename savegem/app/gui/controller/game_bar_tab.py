from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import UISection
from savegem.app.gui.controller import WidgetController


class GameBarTabController(WidgetController):
    """
    Used to rebind tab root widget to home.game_container widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, bar_tab_root: QCustomWidget):
        self._change_widget_parent(bar_tab_root, UISection.HomeSection, "game_container")
