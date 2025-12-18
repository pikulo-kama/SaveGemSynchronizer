from typing import TYPE_CHECKING, Callable, Type

from savegem.app.gui.component import QCustomComponent, CustomComponentMixin
from savegem.app.gui.controller import load_controllers, WidgetController
from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.widget.command.build import WidgetBuildCommand
from savegem.app.gui.widget.command.delete import WidgetDeleteCommand
from savegem.app.gui.widget.command.disable import WidgetDisableCommand
from savegem.app.gui.widget.command.enable import WidgetEnableCommand
from savegem.app.gui.widget.command.refresh import WidgetEventRefreshCommand, WidgetRefreshCommand
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.window import GUI
    from savegem.app.gui.widget.command import WidgetCommand

_logger = get_logger(__name__)


WidgetFilter = Callable[[WidgetMetadata], bool]


class ManagerContext:
    """
    State container used during the execution of widget commands.

    This class acts as a bridge between the WidgetManager and Command objects,
    tracking which widgets should be added or removed during a single
    transactional update of the UI.
    """

    def __init__(self,
                 manager: "WidgetManager",
                 widgets: list[QCustomComponent],
                 controllers: dict[str, WidgetController]):
        """
        Initializes the context with current manager state.

        Args:
            manager: The parent WidgetManager instance.
            widgets: List of currently active widgets in the manager.
            controllers: Mapping of controller names to their instances.
        """

        self.__manager = manager
        self.__widgets = widgets
        self.__controllers = controllers
        self.__new_widgets = []
        self.__removed_widgets = []

    def add_widget(self, widget: QCustomComponent):
        """
        Registers a new widget to be built and added to the UI.

        Args:
            widget: The component instance to be added.
        """
        self.__new_widgets.append(widget)

    def remove_widget(self, widget: QCustomComponent):
        """
        Schedules an existing widget for removal and cleanup.

        Args:
            widget: The component instance to be removed.
        """
        self.__removed_widgets.append(widget)

    @property
    def manager(self) -> "WidgetManager":
        """
        Returns the WidgetManager associated with this context.
        """
        return self.__manager

    @property
    def controllers(self) -> dict[str, WidgetController]:
        """
        Returns the dictionary of available widget controllers.
        """
        return self.__controllers

    @property
    def widgets(self) -> list[QCustomComponent]:
        """
        Returns the list of widgets that existed when the context was created.
        """
        return self.__widgets

    @property
    def new_widgets(self) -> list[QCustomComponent]:
        """
        Returns the list of widgets scheduled for addition.
        """
        return self.__new_widgets

    @property
    def removed_widgets(self) -> list[QCustomComponent]:
        """
        Returns a unique list of widgets scheduled for removal.

        Uses a set internally to ensure that even if a widget was requested
        to be removed multiple times, it is only processed once.
        """
        return list(set(self.__removed_widgets))


class WidgetManager:
    """
    Manages the lifecycle, rendering, and controller invocation for all GUI widgets.
    """

    def __init__(self, gui: "GUI"):
        """
        Initializes the manager and loads the widget controllers.

        Args:
            gui: Reference to the main GUI application.
        """

        self.__gui = gui
        self.__widgets: dict[str, QCustomComponent] = {}
        self.__controllers: dict[str, WidgetController] = load_controllers(self)

    def execute(self, command: "WidgetCommand"):
        """
        Executes a widget command and applies the resulting additions or removals.

        Args:
            command: The command object to execute.
        """

        context = ManagerContext(self, list(self.__widgets.values()), self.__controllers)
        command.execute(context)

        # Add new widgets.
        self.__add_widgets(context.new_widgets)

        # Remove widgets.
        self.__remove_widgets(context.removed_widgets)

    def build(self, metadata: list[WidgetMetadata]):
        """
        Executes a build command for the given metadata list.

        Args:
            metadata: Metadata defining the widgets to build.
        """
        self.execute(WidgetBuildCommand(metadata))

    def refresh(self, widget_filter: WidgetFilter = None):
        """
        Executes a refresh command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets for refreshing.
        """
        self.__execute_with_filter(WidgetRefreshCommand, widget_filter)

    def event_refresh(self, event: str):
        """
        Executes a refresh command triggered by a specific event.

        Args:
            event: The name of the event.
        """
        self.execute(WidgetEventRefreshCommand(event))

    def enable(self, widget_filter: WidgetFilter = None):
        """
        Executes an enable command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to enable.
        """
        self.__execute_with_filter(WidgetEnableCommand, widget_filter)

    def disable(self, widget_filter: WidgetFilter = None):
        """
        Executes a disable command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to disable.
        """
        self.__execute_with_filter(WidgetDisableCommand, widget_filter)

    def delete(self, widget_filter: WidgetFilter = None):
        """
        Executes a delete command using the provided filter.

        Args:
            widget_filter: Optional filter to select widgets to delete.
        """
        self.__execute_with_filter(WidgetDeleteCommand, widget_filter)

    def get_widget(self, section_id: str, widget_id: str):
        """
        Retrieves a widget by its combined section and widget ID.

        Args:
            section_id: The ID of the section.
            widget_id: The ID of the widget.
        """

        widget_name = f"{section_id}.{widget_id}"
        return self.__widgets.get(widget_name)

    def invoke_controllers(self, target: str, widgets: list[QCustomComponent]):
        """
        Calls a specific method on the controllers for the provided widgets.

        Args:
            target: The method name to call on the controller.
            widgets: The widgets whose controllers should be invoked.
        """

        for widget in widgets:
            controller = self.__controllers.get(widget.metadata.controller)

            if controller is None:
                continue

            method = getattr(controller, target)
            method(widget)

    def __execute_with_filter(self, command: Type, widget_filter: WidgetFilter = None):
        """
        Internal helper to execute filter-based commands.

        Args:
            command: The command class to instantiate.
            widget_filter: The filter logic to pass to the command.
        """

        if widget_filter is None:
            widget_filter = lambda meta: True

        self.execute(command(widget_filter))

    def __add_widgets(self, widgets: list[QCustomComponent]):
        """
        Adds widgets to the UI hierarchy and registers them in the manager.

        Args:
            widgets: List of widgets to add.
        """

        for widget in sorted(widgets, key=lambda w: w.metadata.order_id):
            meta = widget.metadata

            if meta.parent_widget_id is None:
                parent_layout = self.__gui.root.layout()
                parent_layout.addWidget(widget)

            else:
                parent = self.__widgets.get(meta.parent_widget_name)

                if parent is None:
                    parent = next((
                        widget for widget in widgets
                        if widget.metadata.name == meta.parent_widget_name
                    ), None)

                widget.metadata.parent = parent.metadata
                parent_layout: QCustomLayout = parent.layout()

                _logger.debug("Adding %s as child of %s", widget.metadata.name, parent.metadata.name)
                parent_layout.add_widget(widget)

            self.__widgets[widget.metadata.name] = widget
            _logger.debug("Widget %s has been added to the manager.", widget.metadata.name)

        self.invoke_controllers("setup", widgets)

    def __remove_widgets(self, widgets: list[QCustomComponent]):
        """
        Removes widgets and their children from the UI and manager registry.

        Args:
            widgets: List of widgets to remove.
        """

        def remove_widget(window_widget: QCustomComponent):
            widget_name = window_widget.metadata.name

            if widget_name not in self.__widgets.keys():
                return

            del self.__widgets[window_widget.metadata.name]

            window_widget.setParent(None)
            window_widget.deleteLater()

        for widget in widgets:
            remove_widget(widget)

            for child in widget.findChildren(CustomComponentMixin):
                remove_widget(child)
