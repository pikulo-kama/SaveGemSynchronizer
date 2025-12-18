from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


class WidgetDisableCommand(FilterWidgetCommand):
    """
    A command that disables a filtered set of widgets and notifies their
    associated controllers.

    This command ensures that both the visual state of the widget and the
    logical state of the controller are synchronized when a component
    is set to a disabled state.
    """

    def execute(self, context: "ManagerContext"):
        """
        Identifies applicable widgets, disables them, and triggers the
        'disable' hook on the corresponding controllers.

        Args:
            context (ManagerContext): The current management context.
        """

        disabled_widgets = []

        for widget in context.widgets:
            if self._is_applicable(widget):
                disabled_widgets.append(widget)
                widget.disable()

        context.manager.invoke_controllers("disable", disabled_widgets)
