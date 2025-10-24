import json
from dataclasses import dataclass
from typing import Final

from PyQt6.QtCore import Qt

from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.widget.type import WidgetType, UIObjectType, get_widget_type, get_layout_type
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseRow


_alignment_map = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "top": Qt.AlignmentFlag.AlignTop,
    "center": Qt.AlignmentFlag.AlignCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "right": Qt.AlignmentFlag.AlignRight,
    "bottom": Qt.AlignmentFlag.AlignBottom
}


"""
Root section name.
This is main section that is being built in the first
place when application starts.
"""
RootSection: Final = "root"


@dataclass
class RefreshEventMetadata:
    """
    Holder for additional
    refresh event metadata.
    """

    refresh_children: bool


class WidgetMetadata:
    """
    Represents widget metadata.
    """

    def __init__(self,
                 widget_id: str,
                 section_id: str,
                 widget_type: WidgetType,
                 layout_type: UIObjectType = None,
                 parent_widget_id: str = None,
                 controller: str = None,
                 order_id: int = None,
                 spacing: int = None,
                 width: int = None,
                 height: int = None,
                 margin_left: int = None,
                 margin_top: int = None,
                 margin_right: int = None,
                 margin_bottom: int = None,
                 object_name: str = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0),
                 content: str = None,
                 tooltip: str = None,
                 stylesheet: str = "",
                 properties: dict = None,
                 refresh_events: list[str] = None,
                 refresh_events_meta: dict[str, RefreshEventMetadata] = None):

        self.__id = widget_id
        self.__section_id = section_id
        self.__parent_widget_id = parent_widget_id
        self.__controller = controller
        self.__order_id = order_id or 0

        self.__widget_type = widget_type
        self.__layout_type = layout_type

        self.__spacing = spacing
        self.__width = width
        self.__height = height
        self.__margin_left = margin_left or 0
        self.__margin_top = margin_top or 0
        self.__margin_right = margin_right or 0
        self.__margin_bottom = margin_bottom or 0
        self.__object_name = object_name
        self.__alignment = alignment
        self.__content = content
        self.__tooltip = tooltip
        self.__stylesheet = stylesheet
        self.__properties = properties or {}
        self.__refresh_events = refresh_events or []
        self.__refresh_event_meta = refresh_events_meta or {}

        # ALL refresh event should always be in list of refresh events.
        self.__refresh_event_meta[UIRefreshEvent.All] = RefreshEventMetadata(False)
        self.__refresh_events.append(UIRefreshEvent.All)
        self.__refresh_events = list(set(self.__refresh_events))

    @classmethod
    def from_database_row(cls, metadata_row: DatabaseRow):
        """
        Static initializer.
        Used to initialize metadata from ui_widgets table record.
        """

        widget_id = metadata_row.get("widget_id")
        section_id = metadata_row.get("section_id")
        refresh_events = []
        refresh_events_meta = {}
        properties: dict = {}
        stylesheet: dict = {}

        if metadata_row.get("properties"):
            properties = json.loads(metadata_row.get("properties"))

        if metadata_row.get("stylesheet"):
            stylesheet = json.loads(metadata_row.get("stylesheet"))

        events = db().table("ui_widget_events") \
            .where("widget_id = ? AND section_id = ?", widget_id, section_id) \
            .retrieve()

        for event in events:
            refresh_event = event.get("refresh_event_id")
            refresh_children = event.get("refresh_children") == 1

            refresh_events.append(refresh_event)
            refresh_events_meta[refresh_event] = RefreshEventMetadata(refresh_children)

        return WidgetMetadata(
            widget_id=widget_id,
            section_id=section_id,
            parent_widget_id=metadata_row.get("parent_widget_id"),
            controller=metadata_row.get("controller"),
            order_id=metadata_row.get("order_id"),
            widget_type=get_widget_type(metadata_row.get("widget_type_id")),
            layout_type=get_layout_type(metadata_row.get("layout_type_id")),
            spacing=metadata_row.get("spacing"),
            width=metadata_row.get("width"),
            height=metadata_row.get("height"),
            margin_left=metadata_row.get("margin_left"),
            margin_top=metadata_row.get("margin_top"),
            margin_right=metadata_row.get("margin_right"),
            margin_bottom=metadata_row.get("margin_bottom"),
            object_name=metadata_row.get("style_object_name"),
            content=metadata_row.get("content"),
            tooltip=metadata_row.get("tooltip"),
            alignment=cls.__parse_alignment(metadata_row.get("alignment")),
            stylesheet=cls.__parse_stylesheet(stylesheet),
            properties=properties,
            refresh_events=refresh_events,
            refresh_events_meta=refresh_events_meta
        )

    @property
    def id(self) -> str:
        """
        Used to get ID of widget.
        """
        return self.__id

    @property
    def name(self) -> str:
        """
        Used to get unique ID of widget.
        Concatenation of section ID and widget ID.

        Example: test_widget in root = root.test_widget
        """
        return f"{self.section_id}.{self.id}"

    @property
    def section_id(self) -> str:
        """
        Used to get ID of section with which
        widget is associated.

        If section id is None then 'root' section would be returned.
        """
        return self.__section_id or RootSection

    @property
    def raw_section_id(self):
        """
        Used to get ID of section with which
        widget is associated.
        """
        return self.__section_id

    @property
    def is_root_section(self) -> bool:
        """
        Used to check whether widget is part
        of the root section.
        """
        return self.__section_id is None

    @property
    def parent_widget_id(self) -> str:
        """
        Used to get ID of parent widget.
        """
        return self.__parent_widget_id

    @property
    def parent_widget_name(self) -> str:
        """
        Used to get unique ID of parent widget.
        """
        return f"{self.section_id}.{self.parent_widget_id}"

    @property
    def controller(self) -> str:
        """
        Used to get name of controller associated
        with widget.
        """
        return self.__controller

    @property
    def order_id(self) -> int:
        """
        Used to get order value
        in which widget would be added to layout of parent widget.
        """
        return self.__order_id

    @property
    def widget_type(self) -> WidgetType:
        """
        Used to get metadata of widget type.
        """
        return self.__widget_type

    @property
    def layout_type(self) -> UIObjectType:
        """
        Used to get metadata of layout type.
        """
        return self.__layout_type

    @property
    def stylesheet(self) -> str:
        """
        Used to get custom widget stylesheet.
        """
        return self.__stylesheet

    @property
    def properties(self) -> dict[str, any]:
        """
        Used to get widget's QT properties.
        """
        return self.__properties

    @property
    def spacing(self) -> int:
        """
        Used to get widget layout spacing.
        """
        return self.__spacing

    @property
    def width(self) -> int:
        """
        Used to get widget width.
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Used to get widget height.
        """
        return self.__height

    @property
    def margin_left(self) -> int:
        """
        Used to get widget's left margin.
        """
        return self.__margin_left

    @property
    def margin_top(self) -> int:
        """
        Used to get widget's top margin.
        """
        return self.__margin_top

    @property
    def margin_right(self) -> int:
        """
        Used to get widget's right margin.
        """
        return self.__margin_right

    @property
    def margin_bottom(self) -> int:
        """
        Used to get widget's bottom margin.
        """
        return self.__margin_bottom

    @property
    def object_name(self) -> str:
        """
        Used to get name of widget's QT
        object name.
        """
        return self.__object_name

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """
        Used to get widget's alignment.
        """
        return self.__alignment

    @property
    def content(self) -> str:
        """
        Used to get widget content.
        """
        return self.__content

    @property
    def tooltip(self) -> str:
        """
        Used to get widget's tooltip.
        """
        return self.__tooltip

    @property
    def refresh_events(self) -> list[str]:
        """
        Used to get list of widget refresh events.
        """
        return self.__refresh_events

    def should_refresh_children(self, event: str):
        """
        Used to check whether for current widget
        provided event expect child widgets to be
        refreshed as well.
        """

        event_meta = self.__refresh_event_meta[event]
        return event_meta.refresh_children

    @staticmethod
    def __parse_alignment(alignment: str) -> Qt.AlignmentFlag:
        """
        Used to parse string alignment and transform it into
        QT alignment object.

        Example: top-left -> Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        """
        alignment_prop = Qt.AlignmentFlag(0)

        if alignment is None:
            return alignment_prop

        for part in alignment.split("-"):
            alignment_prop |= _alignment_map.get(part)

        return alignment_prop

    @staticmethod
    def __parse_stylesheet(stylesheet: dict):
        """
        Used to parse JSON stylesheet of widget
        and transform it into regular string.

        Example: {"color": "red", "padding": "0px"} -> "color: red; padding: 0px"
        """
        stylesheet_string = ""

        for key, value in stylesheet.items():
            stylesheet_string += f"{key}: {value};\n"

        return stylesheet_string
