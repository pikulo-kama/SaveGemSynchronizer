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
    Used to load all the controllers defined in package.
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
    Represents widget controller.
    Controller should be used to extend default
    actions that are being done to the widget during
    application lifecycle.
    """

    def __init__(self, manager: "WidgetManager"):
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
        Used to load section data related to current
        controller.
        """

        self.__sections = db().table("ui_sections") \
            .where("controller = ?", self.__class__.__name__) \
            .order_by("order_id") \
            .retrieve()

        if not self.__sections.is_empty:
            _logger.info("Loaded %d section(s) for controller '%s'", len(self.__sections.rows), self.__class__.__name__)

    def setup(self, widget: QWidget):  # pragma: no cover
        """
        Runs only when widget is being built.
        Should be used to perform preparation actions.
        """
        pass

    def refresh(self, widget: QWidget):  # pragma: no cover
        """
        Runs each time refresh is being initiated.
        Should be used to update dynamic data.
        """
        pass

    def enable(self, widget: QWidget):  # pragma: no cover
        """
        Runs each time widget is being enabled.
        """
        pass

    def disable(self, widget: QWidget):  # pragma: no cover
        """
        Runs each time widget is being disabled.
        """
        pass

    @property
    def manager(self):
        """
        Instance of widget manager
        """
        return self.__manager

    @property
    def sections(self):
        """
        Collection of UI section associated
        with current controller.
        """
        return self.__sections

    def reset_state(self):
        """
        Used to reset controller dynamic state.
        """
        self.__state.clear()

    def _get_state(self, key: str):
        """
        Used to get value from dynamic state.
        """
        return self.__state.get(key)

    def _set_state(self, key: str, value):
        """
        Used to set dynamic state value.
        """
        self.__state[key] = value

    def _change_widget_parent(self, widget: QCustomWidget, target_section_id: str, target_widget_id: str):
        """
        Helper method that allows to move provided image
        to another widget.
        """

        target_widget = self.manager.get_widget(target_section_id, target_widget_id)
        target_layout = target_widget.layout()
        original_layout = widget.layout()

        _logger.debug("Rebinding '%s' to '%s'", widget.metadata.name, target_widget.metadata.name)

        original_layout.removeWidget(widget)
        target_layout.addWidget(widget)

    def _do_work(self, worker: QWorker):
        """
        Used to start worker and store it in
        controller, so it won't be garbage collected.
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
    Dynamic resolver which is used to resolve template
    related tokens.

    Actual resolving of tokens happening inside controller.
    """

    def __init__(self, controller: "TemplateWidgetController", element: Any):
        self.__controller = controller
        self.__element = element

    def resolve(self, value: str, *args, **kw):
        return self.__controller.resolve(self.__element, value, *args, **kw)


class TemplateWidgetController(WidgetController):
    """
    Extended version of widget controller.
    Allows to render and manage complex dynamic list widgets.
    """

    HandlerPrefix: Final = "handle__"

    def __init__(self, manager: "WidgetManager"):
        super().__init__(manager)
        self.__handlers = {}

        for name, member in get_methods(self, lambda method: method.startswith(self.HandlerPrefix)):
            widget_id = name.replace(self.HandlerPrefix, "")
            self.__handlers[widget_id] = member

    def refresh(self, widget: QCustomComponent):
        """
        Used to build template widget.
        Will build header and footer widgets as they're
        defined in metadata.

        As for body widgets they would be built for each element of template
        dataset.
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
        Used to get template dataset.
        For each record of dataset body template would
        be rendered.
        """
        return []

    def resolve(self, element: Any, value: str, *args, **kw):
        """
        Used to resolve template specific tokens.
        This method is being called by dynamic content resolver.

        This method only handles 'template' tokens defined
        in template body segment.
        """
        return value

    def __invoke_widget_handlers(self, segment_root: QCustomComponent, element: Any):
        """
        Used to call handler method to allow additional operations
        over widgets once they were created.
        Handlers are being invoked only for widgets of body segment.

        Example: If you have widget with id 'dynamic_create_button'
        then you should create method with the name 'handle__dynamic_create_button'
        in controller implementation.

        First argument of handler method would be actual widget that was requested
        and the second would element from dataset associated with the widget.
        """

        widgets: list = segment_root.findChildren(CustomComponentMixin)
        widgets.append(segment_root)

        for widget in widgets:
            handler_method = self.__handlers.get(widget.metadata.original_id)

            if handler_method is not None:
                handler_method(widget, element)

    def __segment_metadata(self, section_id: str, widget: QCustomComponent) -> Dict[WidgetMetadata, List[WidgetMetadata]]:
        """
        Used to read template section (segment) metadata
        and then group data by root elements.

        This is necessary for templates since they could have multiple root widgets defined
        which might mess up with the order if segmentation is not performed.
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
        Used to get metadata of root widget
        of requested widget metadata.
        """

        for meta in all_metadata:
            if meta.id == target.parent_widget_id:
                return self.__get_segment_root(meta, all_metadata)

        return target
