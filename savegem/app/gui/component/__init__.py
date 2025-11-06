from typing import Union, Optional

from PyQt6.QtCore import Qt, QObject
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component.layout import QCustomLayout
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.resolver import resolve_content


class CustomComponentMixin:
    """
    Mixin for QT components.
    Used to extend existing QT objects.
    """

    def __init__(self):
        self.__metadata: Optional[WidgetMetadata] = None

    def set_content(self, content):
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

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(True)  # noqa
            self.setCursor(Qt.CursorShape.PointingHandCursor)  # noqa

    def disable(self):
        """
        Used to disable widget.
        """

        if self.metadata.widget_type.is_interactable:
            self.setEnabled(False)  # noqa
            self.setCursor(Qt.CursorShape.WaitCursor)  # noqa

    def refresh(self, refresh_children: bool = False):
        """
        Used to refresh widget's.
        Will also refresh child widgets if requested.
        """

        if self.metadata is None:
            return

        if self.metadata.content is not None:
            self.set_content(resolve_content(self.metadata.content))

        if self.metadata.tooltip is not None:
            self.setToolTip(resolve_content(self.metadata.tooltip))  # noqa

        if refresh_children:
            children = self.findChildren(CustomComponentMixin)  # noqa
            for child_widget in children:
                child_widget.refresh()

    def update_styles(self):

        self.style().polish(self)  # noqa

        for child in self.findChildren(CustomComponentMixin):  # noqa
            child.update_styles()


"""
Type that includes properties of both basic QT
widget and component mixin.
"""
QCustomComponent = Union[QWidget, CustomComponentMixin]
