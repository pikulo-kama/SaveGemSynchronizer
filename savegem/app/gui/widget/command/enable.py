from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


class WidgetEnableCommand(FilterWidgetCommand):
    """
    Used to enable widgets that satisfy widget filter
    and invokes 'enable' handler on related controllers.
    """

    def execute(self, context: "ManagerContext"):
        enabled_widgets = []

        for widget in context.widgets:
            if self._is_applicable(widget):
                enabled_widgets.append(widget)
                widget.enable()

        context.manager.invoke_controllers("enable", enabled_widgets)
