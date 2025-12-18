from typing import TYPE_CHECKING

from savegem.app.gui.widget.command import FilterWidgetCommand
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext

_logger = get_logger(__name__)


class WidgetDeleteCommand(FilterWidgetCommand):
    """
    Used to mark widgets that satisfy widget filter as
    deleted so that widget manager would remove them from
    internal state, unlink from other widgets and then finally
    delete widgets themselves.
    """

    def execute(self, context: "ManagerContext"):

        for widget in context.widgets:

            if not self._is_applicable(widget):
                continue

            controller = context.controllers.get(widget.metadata.controller)

            # Reset controllers' state.
            if controller is not None:
                _logger.debug("Resetting state of %s", widget.metadata.controller)
                controller.reset_state()

            context.remove_widget(widget)
