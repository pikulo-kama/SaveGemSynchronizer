from typing import Union, Optional

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QWidget, QApplication

from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class CustomComponentMixin:
    """
    A mixin class designed to extend standard PyQt6 QWidget objects with
    specific functionality.

    This mixin provides integrated metadata handling, content resolution,
    recursive styling, and custom event filtering for disabled states.
    """

    def __init__(self):
        """
        Initializes the mixin with default state.
        """
        self.__metadata: Optional[WidgetMetadata] = None
        self.__disabled = False

    def set_content(self, content):  # pragma: no cover
        """
        Sets the visual or textual content of the widget.

        This method should be overridden by subclasses to handle specific
        content types (e.g., text or pixmap for labels, icon for buttons, etc.).

        Args:
            content: The resolved content to be applied to the widget.
        """
        pass

    def apply_alignment(self):
        """
        Applies the alignment settings defined in the widget's metadata
        to its internal layout.
        """

        layout = self.layout()  # noqa

        if layout is not None:
            layout.setAlignment(self.metadata.alignment)

    @property
    def metadata(self) -> WidgetMetadata:
        """
        Returns the metadata associated with this component.

        Returns:
            WidgetMetadata: The metadata object containing component configuration.
        """
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata: WidgetMetadata):
        """
        Assigns metadata to the component.

        Args:
            metadata (WidgetMetadata): The configuration metadata to attach.
        """
        self.__metadata = metadata

    def enable(self):
        """
        Enables the widget and restores its interactivity.

        If the widget type is marked as interactable, this restores the
        standard pointer cursor and enables the underlying Qt widget.
        """

        _logger.debug("Enabling widget '%s'", self.metadata.name)
        self.__disabled = False

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(True)  # noqa
            self.setCursor(Qt.CursorShape.PointingHandCursor)  # noqa

    def disable(self):
        """
        Disables the widget and prevents user interaction.

        If the widget type is marked as interactable, this sets the widget
        to a disabled state and resets the cursor to the default window cursor.
        """

        _logger.debug("Disabling widget '%s'", self.metadata.name)
        self.__disabled = True

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(False)  # noqa
            self.setCursor(QApplication.activeWindow().cursor())  # noqa

    def event(self, event: QEvent):
        """
        Filters Qt events to implement custom behavior for disabled components.

        Blocks all pointer-based user interactions (clicks, hovers) when the
        internal disabled flag is set, while allowing system events to pass.

        Args:
            event (QEvent): The Qt event being processed.

        Returns:
            bool: True if the event was handled/blocked, otherwise the
                  result of the base class event handler.
        """

        # Block all pointer (user initiated) events
        # when widget is disabled.
        if self.__disabled and event.isPointerEvent():
            return True

        return super().event(event)  # noqa

    def refresh(self, refresh_children: bool = False):
        """
        Refreshes the widget by re-resolving its content and tooltips.

        Uses the resolver system to update the widget's state based on current
        metadata and environment. Optionally performs a recursive refresh
        on all nested child components.

        Args:
            refresh_children (bool): If True, triggers refresh() on all
                                     descendants that use this mixin.
        """

        if self.metadata is None:
            _logger.error("Instance of widget %s doesn't have metadata in place.", self.__class__.__name__)
            return

        _logger.debug("Refreshing widget '%s'", self.metadata.name)

        if self.metadata.content is not None:
            content = resolve_content(self.metadata.content, extra_resolvers=self.metadata.resolvers)
            self.set_content(content)

            _logger.debug("Content=%s", content)

        if self.metadata.tooltip is not None:
            tooltip = resolve_content(self.metadata.tooltip, extra_resolvers=self.metadata.resolvers)
            self.setToolTip(tooltip)  # noqa

            _logger.debug("Tooltip=%s", tooltip)

        if refresh_children:
            _logger.debug("Refreshing child widgets")
            children = self.findChildren(CustomComponentMixin)  # noqa
            for child_widget in children:
                child_widget.refresh()

    def update_styles(self):
        """
        Forcefully re-applies Qt styles and polishes the component.

        This method is used to trigger a stylesheet re-evaluation. It
        recursively propagates the style update to all child components
        that use this mixin.
        """

        self.style().polish(self)  # noqa

        for child in self.findChildren(CustomComponentMixin):  # noqa
            child.update_styles()

    def __str__(self):
        """
        Returns a string representation of the component for logging/debugging.
        """

        type_name = self.metadata.widget_type.name
        name = self.metadata.name
        order_id = self.metadata.order_id
        parent_name = self.metadata.parent_widget_name

        return f"{type_name}[name: {name}, parent: {parent_name}, order: {order_id}]"


QCustomComponent = Union[QWidget, CustomComponentMixin]
"""
A Type alias representing a valid PyQt widget enhanced with the CustomComponentMixin.
"""
