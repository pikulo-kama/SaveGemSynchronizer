from typing import TYPE_CHECKING

from savegem.app.gui.component import CustomComponentMixin

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import ManagerContext, WidgetFilter


class WidgetCommand:
    """
    Command that is used to perform
    actions against widgets stored in widget manager.
    """

    def execute(self, context: "ManagerContext"):  # pragma: no cover
        """
        Should be used to perform actions on widgets
        that are being passed inside context object.
        """
        pass


class FilterWidgetCommand(WidgetCommand):
    """
    Command that additionally accepts widget filter
    which is used to limit widgets on which command
    would or would not perform operations.
    """

    def __init__(self, widget_filter: "WidgetFilter"):
        self.__widget_filter = widget_filter

    def _is_applicable(self, widget: CustomComponentMixin):
        """
        Used to check whether provided widget satisfies
        widget filter.
        """
        return self.__widget_filter(widget.metadata)
