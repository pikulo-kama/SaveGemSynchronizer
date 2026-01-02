from kui.component.widget import KamaWidget
from kui.core.controller import WidgetController

from savegem.constants import UISection


class GameBarTabController(WidgetController):
    """
    Used to rebind tab root widget to home.game_container widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, bar_tab_root: KamaWidget):
        self._change_widget_parent(bar_tab_root, UISection.HomeSection, "game_container")
