from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext

_logger = get_logger(__name__)


class WidgetDeleteCommand(FilterWidgetCommand):
    """
    A command designed to identify and remove widgets from the application
    based on specific filtering criteria.

    This command handles the cleanup process by resetting the state of
    associated controllers before removing the widget from the management
    context, ensuring no stale data remains in memory.
    """

    def execute(self, context: "ManagerContext"):
        """
        Iterates through active widgets, identifies those matching the filter,
        resets their controllers, and removes them from the context.

        Args:
            context (ManagerContext): The context containing the widgets and
                                      controllers to be processed.
        """

        for widget in context.widgets:

            if not self._is_applicable(widget):
                continue

            controller = context.controllers.get(widget.metadata.controller)

            # Reset controllers' state.
            if controller is not None:
                _logger.debug("Resetting state of %s", widget.metadata.controller)
                controller.reset_state()

            context.remove_widget(widget)
