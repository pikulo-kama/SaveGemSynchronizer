from typing import TYPE_CHECKING

from savegem.app.gui.component import QCustomComponent
from savegem.app.gui.widget.command import FilterWidgetCommand
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


_logger = get_logger(__name__)


class WidgetRefreshCommand(FilterWidgetCommand):
    """
    A command that triggers a data and visual refresh for a filtered set of widgets
    and notifies their associated controllers.

    This command orchestrates the synchronization between the widget's internal
    state (via metadata resolution) and the controller's dynamic data.
    """

    def execute(self, context: "ManagerContext"):
        """
        Processes widgets in the context, applying refreshes where applicable
        and invoking the 'refresh' hook on controllers.

        Args:
            context (ManagerContext): The context containing widgets and the
                                      widget manager.
        """

        refreshed_widgets = []

        for widget in context.widgets:
            refresh_children = self._refresh_children(widget)

            if not self._is_applicable(widget):
                continue

            if refresh_children:
                _logger.debug("Refreshing %s recursively.", widget.metadata.name)

            widget.refresh(refresh_children=refresh_children)
            refreshed_widgets.append(widget)

        _logger.debug("Invoking 'refresh' controllers.")
        context.manager.invoke_controllers("refresh", refreshed_widgets)

    def _refresh_children(self, widget: QCustomComponent):
        """
        Determines if the refresh operation should propagate to the widget's children.

        Args:
            widget (QCustomComponent): The widget to evaluate.

        Returns:
            bool: Always returns False in the base implementation.
        """
        return False


class WidgetEventRefreshCommand(WidgetRefreshCommand):
    """
    A specialized refresh command triggered by specific application events.

    This command filters widgets based on whether they have registered a
    matching event string in their 'refresh_events' metadata.
    """

    def __init__(self, event: str):
        """
        Initializes the command with an event identifier and a filter lambda.

        Args:
            event (str): The unique string identifier of the refresh event.
        """

        super().__init__(lambda meta: event in meta.refresh_events)
        self.__event = event

    def _refresh_children(self, widget: QCustomComponent):
        """
        Checks metadata to see if the specific event should trigger a
        recursive refresh.

        Args:
            widget (QCustomComponent): The widget to evaluate.

        Returns:
            bool: True if children should be refreshed for this event.
        """
        return widget.metadata.should_refresh_children(self.__event)
