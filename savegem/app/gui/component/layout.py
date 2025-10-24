from typing import Optional, Union, TYPE_CHECKING
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLayout
from savegem.app.gui.widget.metadata import WidgetMetadata
from savegem.app.gui.widget.type import get_widget_type

if TYPE_CHECKING:
    from savegem.app.gui.widget.manager import WidgetManager
    from savegem.app.gui.component import QCustomComponent


class CustomLayoutMixin:

    def __init__(self):
        self.__manager: Optional["WidgetManager"] = None

    def set_manager(self, manager: "WidgetManager"):
        self.__manager = manager

    def add_dynamic_widget(self, widget: "QCustomComponent", **kw):
        parent_widget: "QCustomComponent" = self.parentWidget()  # noqa
        parent_meta = parent_widget.metadata
        order_id = self.count()  # noqa

        widget.metadata = WidgetMetadata(
            widget_id=f"{parent_meta.id}_child{order_id}",  # noqa
            section_id=parent_meta.raw_section_id,
            parent_widget_id=parent_meta.id,
            order_id=order_id,  # noqa
            widget_type=get_widget_type(widget.__class__.__name__)
        )

        self.__manager.add_widget(widget)
        self.addWidget(widget, **kw)  # noqa


class QCustomVBoxLayout(QVBoxLayout, CustomLayoutMixin):
    pass


class QCustomHBoxLayout(QHBoxLayout, CustomLayoutMixin):
    pass


class QCustomGridLayout(QGridLayout, CustomLayoutMixin):
    pass


QCustomLayout = Union[QLayout, CustomLayoutMixin]
