from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


class WidgetEnableCommand(FilterWidgetCommand):
    """
    A command that restores interactivity to a filtered set of widgets and
    triggers the 'enable' lifecycle hook on their associated controllers.

    This command acts as the inverse of WidgetDisableCommand, ensuring that
    the UI components and the underlying business logic are reactivated in
    unison.
    """

    def execute(self, context: "ManagerContext"):
        """
        Processes all widgets in the context, enabling those that match the filter
        criteria and notifying the controller manager.

        Args:
            context (ManagerContext): The context containing active widgets and
                                      the widget manager.
        """

        enabled_widgets = []

        for widget in context.widgets:
            if self._is_applicable(widget):
                enabled_widgets.append(widget)
                widget.enable()

        context.manager.invoke_controllers("enable", enabled_widgets)
