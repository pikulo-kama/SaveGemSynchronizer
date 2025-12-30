from kui.component.widget import KamaWidget
from kui.core.controller import WidgetController

from savegem.constants import UISection


class MenuItemController(WidgetController):
    """
    Used to rebind menu item root widget to content widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, section_root_widget: KamaWidget):
        self._change_widget_parent(section_root_widget, UISection.RootSection, "content")
