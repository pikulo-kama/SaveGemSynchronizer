from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import UISection
from savegem.app.gui.controller import WidgetController


class MenuItemController(WidgetController):
    """
    Used to rebind menu item root widget to content widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, section_root_widget: QCustomWidget):
        self._change_widget_parent(section_root_widget, UISection.RootSection, "content")
