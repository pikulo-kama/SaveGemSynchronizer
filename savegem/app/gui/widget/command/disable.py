from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


class WidgetDisableCommand(FilterWidgetCommand):
    """
    Used to disable widgets that satisfy widget filter
    and invokes 'disable' handler on related controllers.
    """

    def execute(self, context: "ManagerContext"):
        disabled_widgets = []

        for widget in context.widgets:
            if self._is_applicable(widget):
                disabled_widgets.append(widget)
                widget.disable()

        context.manager.invoke_controllers("disable", disabled_widgets)
