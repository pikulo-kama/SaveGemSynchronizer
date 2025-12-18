import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Optional, List, Any, Final, Dict

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component import QCustomComponent, CustomComponentMixin
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.thread import execute_in_blocking_thread
from savegem.app.gui.widget.command.build import WidgetSectionBuildCommand
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.resolver import ContentResolver
from savegem.app.worker import QWorker
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseTable
from savegem.common.util.logger import get_logger
from savegem.common.util.reflection import get_members, get_methods

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import WidgetManager

_logger = get_logger(__name__)


def load_controllers(manager: "WidgetManager"):
    """
    Scans the package for WidgetController subclasses and initializes them.

    This function excludes the base TemplateWidgetController to ensure only concrete
    implementations are loaded into the application context.

    Args:
        manager (WidgetManager): The global widget manager instance.

    Returns:
        dict: A mapping of controller names to initialized WidgetController instances.
    """

    controller_map = {}

    for member_name, member in get_members(__package__, WidgetController):

        # Don't include base template controller
        # since it is not concrete implementation.
        if member == TemplateWidgetController:
            continue

        controller: WidgetController = member(manager)
        controller.load_sections()

        controller_map[member_name] = controller

    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug("Controllers have been loaded: %s", ", ".join(controller_map.keys()))

    return controller_map


class WidgetController:
    """
    Base controller class for managing widget lifecycles and business logic.

    Controllers act as the bridge between the UI components and the application logic,
    handling setup, refresh, and state management. They are persistent for the
    duration of the application.
    """

    def __init__(self, manager: "WidgetManager"):
        """
        Initializes the controller with a reference to the WidgetManager.
        """

        self.__manager = manager

        self.__thread: QThread
        self.__worker: QWorker

        # Dynamic controller state.
        # Since controllers are being created
        # only once when application starts we can't
        # use instance variables to store some data
        # since after widget refreshed it could be not
        # valid anymore, because of this we need to be able
        # to clear this data when refresh is happening.
        self.__state = {}
        self.__sections: Optional[DatabaseTable] = None

    def load_sections(self):
        """
        Retrieves UI section metadata from the database for sections associated
        with this specific controller.
        """

        self.__sections = db().table("ui_sections") \
            .where("controller = ?", self.__class__.__name__) \
            .order_by("order_id") \
            .retrieve()

        if not self.__sections.is_empty:
            _logger.info("Loaded %d section(s) for controller '%s'", len(self.__sections.rows), self.__class__.__name__)

    def setup(self, widget: QWidget):  # pragma: no cover
        """
        Hook called during the initial construction of the widget.
        """
        pass

    def refresh(self, widget: QWidget):  # pragma: no cover
        """
        Hook called whenever the widget requires a data refresh.
        """
        pass

    def enable(self, widget: QWidget):  # pragma: no cover
        """
        Hook called when the widget is transitioned to an enabled state.
        """
        pass

    def disable(self, widget: QWidget):  # pragma: no cover
        """
        Hook called when the widget is transitioned to a disabled state.
        """
        pass

    @property
    def manager(self):
        """
        Returns the WidgetManager instance.
        """
        return self.__manager

    @property
    def sections(self):
        """
        Returns the database rows for sections managed by this controller.
        """
        return self.__sections

    def reset_state(self):
        """
        Clears the dynamic state dictionary.
        """
        self.__state.clear()

    def _get_state(self, key: str):
        """
        Retrieves a value from the dynamic controller state.
        """
        return self.__state.get(key)

    def _set_state(self, key: str, value):
        """
        Stores a value in the dynamic controller state.
        """
        self.__state[key] = value

    def _change_widget_parent(self, widget: QCustomWidget, target_section_id: str, target_widget_id: str):
        """
        Moves a widget from its current layout to the layout of a target widget.

        Args:
            widget (QCustomWidget): The widget to move.
            target_section_id (str): Section ID of the new parent.
            target_widget_id (str): Widget ID of the new parent.
        """

        target_widget = self.manager.get_widget(target_section_id, target_widget_id)
        target_layout = target_widget.layout()
        original_layout = widget.layout()

        _logger.debug("Rebinding '%s' to '%s'", widget.metadata.name, target_widget.metadata.name)

        original_layout.removeWidget(widget)
        target_layout.addWidget(widget)

    def _do_work(self, worker: QWorker):
        """
        Executes a background worker in a separate blocking thread.

        Args:
            worker (QWorker): The worker instance containing the logic to execute.
        """

        self.__thread = QThread()
        self.__worker = worker

        _logger.debug(
            "Starting %s worker from controller %s",
            self.__worker.__class__.__name__,
            self.__class__.__name__
        )
        execute_in_blocking_thread(self.__thread, self.__worker)


class TemplateResolver(ContentResolver):
    """
    A specialized resolver for handling tokens within dynamic templates.

    This class delegates the actual resolution logic back to the
    TemplateWidgetController, providing context for the specific element
    being rendered.
    """

    def __init__(self, controller: "TemplateWidgetController", element: Any):
        """
        Initializes the resolver with a controller and the data element context.
        """

        self.__controller = controller
        self.__element = element

    def resolve(self, value: str, *args, **kw):
        """
        Resolves a string value using the associated controller.
        """
        return self.__controller.resolve(self.__element, value, *args, **kw)


class TemplateWidgetController(WidgetController):
    """
    Advanced controller for rendering dynamic repeated UI elements (lists).

    It divides a template into header, body, and footer segments, duplicating
    the body segment for every item in a provided dataset.
    """

    HandlerPrefix: Final = "handle__"

    def __init__(self, manager: "WidgetManager"):
        """
        Initializes the template controller and maps handler methods for dynamic widgets.
        """

        super().__init__(manager)
        self.__handlers = {}

        for name, member in get_methods(self, lambda method: method.startswith(self.HandlerPrefix)):
            widget_id = name.replace(self.HandlerPrefix, "")
            self.__handlers[widget_id] = member

    def refresh(self, widget: QCustomComponent):
        """
        Orchestrates the building of the template structure.

        Cleans up existing dynamic widgets and iterates through the dataset to
        construct the repeated body segments, applying unique IDs and
        contextual resolvers to each.

        Args:
            widget (QCustomComponent): The parent widget containing the template.
        """

        header_section = f"{widget.metadata.id}__template_header"
        body_section = f"{widget.metadata.id}__template_body"
        footer_section = f"{widget.metadata.id}__template_footer"

        header_segments = self.__segment_metadata(header_section, widget)
        body_segments = self.__segment_metadata(body_section, widget)
        footer_segments = self.__segment_metadata(footer_section, widget)

        self.manager.delete(lambda meta: meta.section_id in (header_section, body_section, footer_section))

        # Build header widgets.
        for metadata in header_segments.values():
            self.manager.build(metadata)

        for idx, element in enumerate(self._get_data()):
            body_segments_copy = deepcopy(body_segments)
            template_resolver = TemplateResolver(self, element)

            for root_meta, metadata in body_segments_copy.items():
                widget_count = len(metadata) * len(body_segments)

                # Modify metadata so we won't have widgets with
                # the same ID.
                for widget_meta in metadata:
                    widget_meta.order_id = widget_count * idx + widget_meta.order_id
                    widget_meta.id = f"{widget_meta.original_id}__{idx}"
                    widget_meta.add_resolver(template_resolver)

                    # We need to update parent widget ID as well
                    # so that we can link widgets to correct parents.
                    # We're not setting widget_id if parent is populated,
                    # which should be populated only for root template widgets
                    # that are linked to the input widget itself.
                    if widget_meta.parent is None:
                        widget_meta.parent_widget_id = f"{widget_meta.parent_widget_id}__{idx}"

                # Build actual widgets for segment.
                self.manager.build(metadata)
                segment_root = self.manager.get_widget(body_section, f"{root_meta.original_id}__{idx}")

                self.__invoke_widget_handlers(segment_root, element)

        # Build footer.
        for metadata in footer_segments.values():
            self.manager.build(metadata)

    def _get_data(self) -> list[Any]:
        """
        Retrieves the dataset used to populate the template.
        """
        return []

    def resolve(self, element: Any, value: str, *args, **kw):
        """
        Logic for resolving template-specific tokens based on the current data element.
        """
        return value

    def __invoke_widget_handlers(self, segment_root: QCustomComponent, element: Any):
        """
        Automatically calls 'handle__' methods for widgets within a generated segment.

        Args:
            segment_root (QCustomComponent): The root of the newly created segment.
            element (Any): The data element from the dataset for this segment.
        """

        widgets: list = segment_root.findChildren(CustomComponentMixin)
        widgets.append(segment_root)

        for widget in widgets:
            handler_method = self.__handlers.get(widget.metadata.original_id)

            if handler_method is not None:
                handler_method(widget, element)

    def __segment_metadata(self, section_id: str, widget: QCustomComponent) \
            -> Dict[WidgetMetadata, List[WidgetMetadata]]:
        """
        Groups metadata into logical segments based on their root ancestors.
        """

        metadata = WidgetSectionBuildCommand.retrieve_metadata(section_id)
        grouped_widgets = {}

        for widget_meta in metadata:
            segment_root = self.__get_segment_root(widget_meta, metadata)
            segment_widgets = grouped_widgets.get(segment_root)

            segment_root.parent = widget.metadata

            if segment_widgets is None:
                segment_widgets = []

            segment_widgets.append(widget_meta)
            grouped_widgets[segment_root] = segment_widgets

        return grouped_widgets

    def __get_segment_root(self, target: WidgetMetadata, all_metadata: list[WidgetMetadata]) -> WidgetMetadata:
        """
        Recursively finds the top-level metadata object for a given widget metadata.
        """

        for meta in all_metadata:
            if meta.id == target.parent_widget_id:
                return self.__get_segment_root(meta, all_metadata)

        return target
