from PyQt6.QtWidgets import QWidget

from savegem.app.gui.controller import WidgetController


class MenuItemController(WidgetController):
    """
    Used to rebind menu item root widget to content widget.
    Controller should be assigned only to section root nodes.
    """

    def setup(self, section_root_widget: QWidget):
        self._change_widget_parent(section_root_widget, "root.content")
