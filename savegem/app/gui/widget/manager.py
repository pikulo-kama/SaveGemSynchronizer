import copy
from typing import TYPE_CHECKING, Callable

from savegem.app.gui.component import QCustomComponent
from savegem.app.gui.constants import UIRefreshEvent, UISection
from savegem.app.gui.controller import load_controllers, WidgetController
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseRow
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.app.gui.window import GUI


_logger = get_logger(__name__)


class WidgetManager:
    """
    Used to render and manage lifecycle of
    all widgets that are drawn on the window.
    """

    def __init__(self, gui: "GUI"):
        self.__gui = gui
        self.__widgets: dict[str, QCustomComponent] = {}
        self.__controllers: dict[str, WidgetController] = load_controllers(self)

    @property
    def gui(self):
        """
        Instance of GUI.
        """
        return self.__gui

    def get_widget(self, section_id: str, widget_id: str):
        """
        Used to get widget by its unique ID.
        """

        widget_name = f"{section_id}.{widget_id}"
        return self.__widgets.get(widget_name)

    def add_widget(self, widget: QCustomComponent):
        """
        Used to add register widget in manager.
        """
        self.__widgets[widget.metadata.name] = widget
        _logger.debug("Widget %s has been added to the manager.", widget.metadata.name)

    def build(self, section_id: str = UISection.RootSection):
        """
        Used to build all widgets that
        are part of provided section.
        """

        ui_widgets = db().table("ui_widgets")

        if section_id == UISection.RootSection:
            ui_widgets.where("section_id IS NULL")

        else:
            ui_widgets.where("section_id = ?", section_id)

        # Build widgets.
        for widget_row in ui_widgets.retrieve():
            widget = self.__build_widget(widget_row)
            widget_layout: "QCustomLayout" = widget.layout()

            if widget_layout is not None:
                widget_layout.set_manager(self)

            self.add_widget(widget)

        # Link built widgets together.
        for widget in sorted(self.__widgets.values(), key=lambda w: w.metadata.order_id):
            meta = widget.metadata

            if meta.section_id != section_id:
                continue

            if meta.parent_widget_id is None:
                parent_layout = self.__gui.root.layout()
                parent_layout.addWidget(widget)

            else:
                parent = self.__widgets.get(meta.parent_widget_name)
                parent_layout: QCustomLayout = parent.layout()

                _logger.debug("Adding %s as child of %s", widget.metadata.name, parent.metadata.name)
                parent_layout.add_widget(widget)

        _logger.debug("Invoking 'setup' controllers.")
        self.__invoke_controllers(
            lambda controller, window_widget: controller.setup(window_widget),
            section_id
        )

    def refresh(self, event: str = UIRefreshEvent.All):
        """
        Used to refresh all registered widgets that
        have provided event configured.
        """

        def refresh_invoker(controller: WidgetController, window_widget: QCustomComponent):
            if event in window_widget.metadata.refresh_events:
                controller.refresh(window_widget)

        for widget in self.__widgets.values():
            if event in widget.metadata.refresh_events:
                refresh_children = widget.metadata.should_refresh_children(event)

                if refresh_children:
                    _logger.debug("Refreshing %s recursively.", widget.metadata.name)

                widget.refresh(refresh_children=refresh_children)

        _logger.debug("Invoking 'refresh' controllers.")
        self.__invoke_controllers(refresh_invoker)

    def enable(self):
        """
        Used to enable all registered widgets.
        """

        for widget in self.__widgets.values():
            widget.enable()

        _logger.debug("Invoking 'enable' controllers.")
        self.__invoke_controllers(lambda controller, window_widget: controller.enable(window_widget))

    def disable(self):
        """
        Used to disable all registered widgets.
        """

        for widget in self.__widgets.values():
            widget.disable()

        _logger.debug("Invoking 'disable' controllers.")
        self.__invoke_controllers(lambda controller, window_widget: controller.disable(window_widget))

    def remove_child_widgets(self, widget: QCustomComponent):
        """
        Used to remove all child widgets of provided widget
        from manager.

        Will not remove provided widget itself.
        """

        _logger.debug("Removing child widgets for %s", widget.metadata.name)
        self.remove_widgets(lambda meta: meta.parent_widget_name == widget.metadata.name)

    def remove_widgets(self, clear_condition_function):
        """
        Used to remove all widgets from manager
        whose metadata match provided condition.
        """

        all_widget_meta = copy.deepcopy([widget.metadata for widget in self.__widgets.values()])

        # Remove widget references in
        for meta in all_widget_meta:
            if clear_condition_function(meta):
                controller = self.__controllers.get(meta.controller)

                # Reset controllers' state.
                if controller is not None:
                    _logger.debug("Resetting state of %s", meta.controller)
                    controller.reset_state()

                widget = self.__widgets.get(meta.name)

                if widget is None:
                    continue

                # Remove widget from manager and then remove its children.
                del self.__widgets[meta.name]
                self.remove_widgets(lambda m: m.parent_widget_name == meta.name)

                _logger.debug("Removing %s from manager.", widget.metadata.name)
                widget.setParent(None)
                widget.deleteLater()

    def __invoke_controllers(self, invoker: Callable[[WidgetController, QCustomComponent], None],
                             section_id: str = None):
        """
        Used to invoke all configured controllers.
        If section ID is not provided will invoke controllers
        of all registered widgets, otherwise only those that
        are related to provided section.
        """

        processed_widgets = set()

        # This needs to be infinite loop since invoking controllers
        # may add new widgets to manager which will result in error
        # when we are iterating over them.
        while True:
            widgets_to_process = set()

            # Collect all widgets that have controller assigned.
            # If it's setup stage then only setup of specific section would be performed.
            for widget in self.__widgets.values():

                if widget in processed_widgets:
                    continue

                if widget.metadata.controller is None:
                    continue

                if section_id is not None and widget.metadata.section_id != section_id:
                    continue

                widgets_to_process.add(widget)

            if len(widgets_to_process) == 0:
                break

            # Invoke controllers.
            for window_widget in widgets_to_process:
                controller = self.__controllers.get(window_widget.metadata.controller)

                _logger.debug("Invoking %s for %s", window_widget.metadata.controller, window_widget.metadata.name)
                invoker(controller, window_widget)
                processed_widgets.add(window_widget)

    @staticmethod
    def __build_widget(widget_row: DatabaseRow) -> QCustomComponent:
        """
        Used to build widget based on metadata row.
        """

        meta = WidgetMetadata.from_database_row(widget_row)
        widget: QCustomComponent = meta.widget_type.type()
        widget.metadata = meta

        _logger.debug("Building widget %s", widget.metadata.name)
        _logger.debug("type=%s", widget.metadata.widget_type.name)

        if meta.layout_type is not None:
            _logger.debug("layout=%s", meta.layout_type.name)

            widget.setLayout(meta.layout_type.type())
            widget.layout().setContentsMargins(
                meta.margin_left,
                meta.margin_top,
                meta.margin_right,
                meta.margin_bottom
            )

            if meta.spacing is not None:
                widget.layout().setSpacing(meta.spacing)

        widget.apply_alignment()

        if meta.content is not None:
            _logger.debug("content=%s", meta.content)
            widget.set_content(resolve_content(meta.content))

        if meta.tooltip is not None:
            _logger.debug("tooltip=%s", meta.tooltip)
            widget.setToolTip(resolve_content(meta.tooltip))

        if meta.object_name is not None:
            _logger.debug("object_name=%s", meta.object_name)
            widget.setObjectName(meta.object_name)

        _logger.debug("Setting properties")
        for key, value in meta.properties.items():
            _logger.debug("%s=%s", key, value)
            widget.setProperty(key, value)

        if len(meta.stylesheet) > 0:
            _logger.debug("stylesheet=%s", meta.stylesheet)
            widget.setStyleSheet(meta.stylesheet)

        if meta.width:
            _logger.debug("width=%d", meta.width)
            widget.setFixedWidth(meta.width)

        if meta.height:
            _logger.debug("height=%d", meta.height)
            widget.setFixedHeight(meta.height)

        return widget
