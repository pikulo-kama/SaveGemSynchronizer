from typing import Union, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)

class CustomComponentMixin:
    """
    Mixin for QT components.
    Used to extend existing QT objects.
    """

    def __init__(self):
        self.__metadata: Optional[WidgetMetadata] = None

    def set_content(self, content):  # pragma: no cover
        """
        Used to set content of widget.
        Will set either text or pixmap
        depending on component itself and type of content.
        """
        pass

    def apply_alignment(self):
        """
        Used to apply alignment specified in
        metadata to the widget.
        """

        layout = self.layout()  # noqa

        if layout is not None:
            layout.setAlignment(self.metadata.alignment)

    @property
    def metadata(self) -> WidgetMetadata:
        """
        Used to get widget metadata.
        """
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata: WidgetMetadata):
        """
        Used to set widget metadata.
        """
        self.__metadata = metadata

    def enable(self):
        """
        Used to enable widget.
        """

        _logger.debug("Enabling widget '%s'", self.metadata.name)

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(True)  # noqa
            self.setCursor(Qt.CursorShape.PointingHandCursor)  # noqa

    def disable(self):
        """
        Used to disable widget.
        """

        _logger.debug("Disabling widget '%s'", self.metadata.name)

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(False)  # noqa
            self.setCursor(Qt.CursorShape.WaitCursor)  # noqa

    def refresh(self, refresh_children: bool = False):
        """
        Used to refresh widget's.
        Will also refresh child widgets if requested.
        """

        if self.metadata is None:
            _logger.error("Instance of widget %s doesn't have metadata in place.", self.__class__.__name__)
            return

        _logger.debug("Refreshing widget '%s'", self.metadata.name)

        if self.metadata.content is not None:
            content = resolve_content(self.metadata.content)
            self.set_content(content)

            _logger.debug("Content=%s", content)

        if self.metadata.tooltip is not None:
            tooltip = resolve_content(self.metadata.tooltip)
            self.setToolTip(tooltip)  # noqa

            _logger.debug("Tooltip=%s", tooltip)

        if refresh_children:
            _logger.debug("Refreshing child widgets")
            children = self.findChildren(CustomComponentMixin)  # noqa
            for child_widget in children:
                child_widget.refresh()

    def update_styles(self):
        """
        Used to reload components and reapply styles to them.
        Recursively updates child components.
        """

        self.style().polish(self)  # noqa

        for child in self.findChildren(CustomComponentMixin):  # noqa
            child.update_styles()


"""
Type that includes properties of both basic QT
widget and component mixin.
"""
QCustomComponent = Union[QWidget, CustomComponentMixin]
