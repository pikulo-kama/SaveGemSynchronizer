from typing import Union, TYPE_CHECKING
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLayout

if TYPE_CHECKING:
    from savegem.app.gui.component import QCustomComponent


class CustomLayoutMixin:
    """
    Mixin for QT layouts.
    Used to extend existing QT objects.
    """

    def add_widget(self, widget: "QCustomComponent", **kw):
        """
        Used to add widget to the layout.
        """
        self.addWidget(widget, **kw)  # noqa


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
        order_id = self.count()  # noqa

        # Make sure columns have equal weight
        # so that when there are fewer widgets than
        # amount of configured columns it will not fill
        # all available space.
        for column_id in range(grid_columns):
            self.setColumnStretch(column_id, 1)

        row = order_id // grid_columns
        column = order_id % grid_columns

        self.addWidget(widget, row, column, **kw)  # noqa


QCustomLayout = Union[QLayout, CustomLayoutMixin]
