from typing import Optional, Union, TYPE_CHECKING
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLayout
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.type import get_widget_type_by_class

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import WidgetManager
    from savegem.app.gui.component import QCustomComponent


class CustomLayoutMixin:
    """
    Mixin for QT layouts.
    Used to extend existing QT objects.
    """

    def __init__(self):
        self.__manager: Optional["WidgetManager"] = None

    def set_manager(self, manager: "WidgetManager"):
        """
        Used to link instance of widget manager
        to layout.
        """
        self.__manager = manager

    def add_widget(self, widget: "QCustomComponent", **kw):
        """
        Used to add widget to the layout.
        """
        self.addWidget(widget, **kw)  # noqa

    def add_dynamic_widget(self, widget: "QCustomComponent", **kw):
        """
        Used to add widget to the layout.
        Will also register widget in widget manager.
        """

        parent_widget: "QCustomComponent" = self.parentWidget()  # noqa
        parent_meta = parent_widget.metadata
        order_id = self.count() + 1  # noqa

        widget.metadata = WidgetMetadata(
            widget_id=f"{parent_meta.id}_child{order_id}",  # noqa
            section_id=parent_meta.raw_section_id,
            parent_widget_id=parent_meta.id,
            order_id=order_id,  # noqa
            widget_type=get_widget_type_by_class(widget.__class__)
        )

        widget_layout: QCustomLayout = widget.layout()

        # Propagate widget manager when
        # dynamically adding new elements.
        if widget_layout is not None:
            widget_layout.set_manager(self.__manager)

        self.__manager.add_widget(widget)
        self.add_widget(widget, **kw)


class QCustomVBoxLayout(QVBoxLayout, CustomLayoutMixin):
    """
    Custom vertical layout.
    """
    pass


class QCustomHBoxLayout(QHBoxLayout, CustomLayoutMixin):
    """
    Custom horizontal layout.
    """
    pass


class QCustomGridLayout(QGridLayout, CustomLayoutMixin):
    """
    Custom grid layout.
    """

    def add_widget(self, widget: "QCustomComponent", **kw):
        """
        Adds widget to the layout also checks
        grid columns in layout configuration
        to determine where child widget should be
        placed.
        """

        parent_widget: "QCustomComponent" = self.parentWidget()  # noqa
        parent_meta = parent_widget.metadata

        grid_columns = parent_meta.grid_columns
        # Order of widget starts with 1.
        # We need to make it 0 based.
        order_id = widget.metadata.order_id - 1

        # Make sure columns have equal weight
        # so that when there are less widgets than
        # amount of configured columns it will not fill
        # all available space.
        for column_id in range(grid_columns):
            self.setColumnStretch(column_id, 1)

        row = order_id // grid_columns
        column = order_id % grid_columns

        self.addWidget(widget, row, column, **kw)  # noqa


QCustomLayout = Union[QLayout, CustomLayoutMixin]
