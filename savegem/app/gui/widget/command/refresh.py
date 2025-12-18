from typing import TYPE_CHECKING

from savegem.app.gui.component import QCustomComponent
from savegem.app.gui.widget.command import FilterWidgetCommand
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext


_logger = get_logger(__name__)


class WidgetRefreshCommand(FilterWidgetCommand):
    """
    Used to refresh widgets that satisfy widget filter
    and invokes 'refresh' handler on related controllers.
    """

    def execute(self, context: "ManagerContext"):
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
        Used to check whether provided widgets needs
        to be refreshed recursively with all its children.
        """
        return False


class WidgetEventRefreshCommand(WidgetRefreshCommand):
    """
    Used to refresh all widgets that have provided
    refresh event configured.
    """

    def __init__(self, event: str):
        super().__init__(lambda meta: event in meta.refresh_events)
        self.__event = event

    def _refresh_children(self, widget: QCustomComponent):
        return widget.metadata.should_refresh_children(self.__event)
