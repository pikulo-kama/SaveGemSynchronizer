import json
import re
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import Qt

from savegem.app.gui.constants import UIRefreshEvent, UISection
from savegem.app.gui.style import resolve_style_properties
from savegem.app.gui.widget.resolver import ContentResolver
from savegem.app.gui.widget.type import WidgetType, UIObjectType, get_widget_type, get_layout_type
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseRow
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


_alignment_map = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "top": Qt.AlignmentFlag.AlignTop,
    "center": Qt.AlignmentFlag.AlignCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "right": Qt.AlignmentFlag.AlignRight,
    "bottom": Qt.AlignmentFlag.AlignBottom
}


@dataclass
class RefreshEventMetadata:
    """
    Holder for additional refresh event metadata, such as propagation behavior.
    """

    refresh_children: bool


class WidgetMetadata:
    """
    A comprehensive data container representing the configuration and state of a
    UI widget as defined in the system.

    This class handles the parsing of styles, alignments, layouts, and event
    registrations, acting as the primary blueprint used by WidgetBuilders to
    instantiate and configure QCustomComponents.
    """

    def __init__(self,
                 widget_id: str,
                 section_id: str,
                 widget_type: WidgetType,
                 layout_type: UIObjectType = None,
                 grid_columns: int = None,
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
                 style_object_name: str = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag(0),
                 content: str = None,
                 tooltip: str = None,
                 stylesheet: str = "",
                 properties: dict[str, str] = None,
                 refresh_events: list[str] = None,
                 refresh_events_meta: dict[str, RefreshEventMetadata] = None):
        """
        Initializes a metadata instance with layout, style, and lifecycle parameters.
        """

        self.__id = widget_id
        self.__original_id = widget_id
        self.__section_id = section_id
        self.__parent_widget_id = parent_widget_id
        self.__parent: Optional[WidgetMetadata] = None
        self.__controller = controller
        self.__order_id = order_id or 0

        self.__widget_type = widget_type
        self.__layout_type = layout_type

        self.__grid_columns = grid_columns
        self.__spacing = spacing
        self.__width = width
        self.__height = height
        self.__margin_left = margin_left or 0
        self.__margin_top = margin_top or 0
        self.__margin_right = margin_right or 0
        self.__margin_bottom = margin_bottom or 0
        self.__alignment = alignment
        self.__content = content
        self.__tooltip = tooltip
        self.__stylesheet = resolve_style_properties(stylesheet)
        self.__properties = properties or {}
        self.__refresh_events = refresh_events or []
        self.__refresh_event_meta = refresh_events_meta or {}
        self.__resolvers: list[ContentResolver] = []

        self.__object_name = None
        self.__parse_style_object_name(style_object_name)

        # ALL refresh event should always be in list of refresh events.
        self.__refresh_event_meta[UIRefreshEvent.All] = RefreshEventMetadata(False)
        self.__refresh_events.append(UIRefreshEvent.All)
        self.__refresh_events = list(set(self.__refresh_events))

    @classmethod
    def from_database_row(cls, metadata_row: DatabaseRow):
        """
        Constructs a WidgetMetadata instance from 'ui_widgets' database record,
        resolving linked events and nested styling.

        Args:
            metadata_row (DatabaseRow): A record from the ui_widgets table.

        Returns:
            WidgetMetadata: The hydrated metadata object.
        """

        widget_id = metadata_row.get("widget_id")
        section_id = metadata_row.get("section_id")
        refresh_events = []
        refresh_events_meta = {}
        stylesheet: dict = {}

        if metadata_row.get("stylesheet"):
            stylesheet = json.loads(metadata_row.get("stylesheet"))

        events = db().table("ui_widget_events")

        if section_id is None:
            events.where("widget_id = ? AND section_id IS NULL", widget_id)

        else:
            events.where("widget_id = ? AND section_id = ?", widget_id, section_id)

        for event in events.retrieve():
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
            grid_columns=metadata_row.get("grid_columns"),
            spacing=metadata_row.get("spacing"),
            width=metadata_row.get("width"),
            height=metadata_row.get("height"),
            margin_left=metadata_row.get("margin_left"),
            margin_top=metadata_row.get("margin_top"),
            margin_right=metadata_row.get("margin_right"),
            margin_bottom=metadata_row.get("margin_bottom"),
            style_object_name=metadata_row.get("style_object_name"),
            content=metadata_row.get("content"),
            tooltip=metadata_row.get("tooltip"),
            alignment=cls.__parse_alignment(metadata_row.get("alignment")),
            stylesheet=cls.__parse_stylesheet(stylesheet),
            refresh_events=refresh_events,
            refresh_events_meta=refresh_events_meta
        )

    @property
    def id(self) -> str:
        """
        Retrieves the current unique ID of the widget.
        """
        return self.__id

    @id.setter
    def id(self, widget_id: str):
        """
        Sets a new unique ID for the widget.
        """
        self.__id = widget_id

    @property
    def original_id(self):
        """
        Retrieves the original ID defined in the database, useful for
        identifying template segments.
        """
        return self.__original_id

    @property
    def name(self) -> str:
        """
        Returns a qualified name combining the section ID and widget ID.
        """
        return f"{self.section_id}.{self.id}"

    @property
    def section_id(self) -> str:
        """
        Retrieves the section ID, defaulting to 'root' if none is specified.
        """
        return self.__section_id or UISection.RootSection

    @property
    def raw_section_id(self):
        """
        Retrieves the original section ID without root-fallback.
        """
        return self.__section_id

    @property
    def is_root_section(self) -> bool:
        """
        Checks if the widget belongs to the root UI section.
        """
        return self.__section_id is None

    @property
    def parent(self) -> "WidgetMetadata":
        """
        Retrieves the parent metadata object if linked.
        """
        return self.__parent

    @parent.setter
    def parent(self, parent: "WidgetMetadata"):
        """
        Links a parent metadata object to this instance.
        """
        self.__parent = parent

    @property
    def parent_widget_id(self) -> str:
        """
        Retrieves the ID of the parent widget container.
        """

        if self.parent is not None:
            return self.parent.id

        return self.__parent_widget_id

    @parent_widget_id.setter
    def parent_widget_id(self, parent_widget_id: str):
        """
        Sets the ID of the parent widget container.
        """
        self.__parent_widget_id = parent_widget_id

    @property
    def parent_widget_name(self) -> str:
        """
        Returns the qualified name of the parent widget.
        """

        if self.parent is not None:
            return self.parent.name

        return f"{self.section_id}.{self.parent_widget_id}"

    @property
    def controller(self) -> str:
        """
        Retrieves the name of the associated controller class.
        """
        return self.__controller

    @property
    def resolvers(self) -> dict[str, ContentResolver]:
        """
        Returns a mapping of resolver names to instances associated with this widget.
        """

        resolvers = {}

        for resolver in self.__resolvers:
            resolver_name = str(resolver.__class__.__name__).lower()
            resolvers[resolver_name] = resolver

        return resolvers

    def add_resolver(self, resolver: ContentResolver):
        """
        Registers a new content resolver for dynamic token resolution.
        """
        self.__resolvers.append(resolver)

    @property
    def order_id(self) -> int:
        """
        Retrieves the sorting order for placement within a layout.
        """
        return self.__order_id

    @order_id.setter
    def order_id(self, order_id: int):
        """
        Sets the sorting order for layout placement.
        """
        self.__order_id = order_id

    @property
    def widget_type(self) -> WidgetType:
        """
        Retrieves the type metadata (e.g., QPushButton, QLabel).
        """
        return self.__widget_type

    @property
    def layout_type(self) -> UIObjectType:
        """
        Retrieves the layout metadata (e.g., QVBoxLayout).
        """
        return self.__layout_type

    @property
    def grid_columns(self) -> int:
        """
        Retrieves the column count for grid layouts.
        """
        return self.__grid_columns

    @property
    def stylesheet(self) -> str:
        """
        Retrieves the generated QSS stylesheet string.
        """
        return self.__stylesheet

    @property
    def properties(self) -> dict[str, str]:
        """
        Retrieves dynamic properties used for QSS targeting.
        """
        return self.__properties

    @property
    def spacing(self) -> int:
        """
        Retrieves the internal spacing of the widget's layout.
        """
        return self.__spacing

    @property
    def width(self) -> int:
        """
        Retrieves the fixed width of the widget.
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        Retrieves the fixed height of the widget.
        """
        return self.__height

    @property
    def margin_left(self) -> int:
        """
        Retrieves the left layout margin.
        """
        return self.__margin_left

    @property
    def margin_top(self) -> int:
        """
        Retrieves the top layout margin.
        """
        return self.__margin_top

    @property
    def margin_right(self) -> int:
        """
        Retrieves the right layout margin.
        """
        return self.__margin_right

    @property
    def margin_bottom(self) -> int:
        """
        Retrieves the bottom layout margin.
        """
        return self.__margin_bottom

    @property
    def object_name(self) -> str:
        """
        Retrieves the Qt internal object name for QSS identification.
        """
        return self.__object_name

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """
        Retrieves the alignment flag for the widget's content.
        """
        return self.__alignment

    @property
    def content(self) -> str:
        """
        Retrieves the raw content/text value of the widget.
        """
        return self.__content

    @property
    def tooltip(self) -> str:
        """
        Retrieves the tooltip text.
        """
        return self.__tooltip

    @property
    def refresh_events(self) -> list[str]:
        """
        Retrieves the list of events that trigger a refresh for this widget.
        """
        return self.__refresh_events

    def should_refresh_children(self, event: str):
        """
        Checks if a specific event requires recursive child refreshing.

        Args:
            event (str): The event identifier.

        Returns:
            bool: True if children should be refreshed.
        """

        event_meta = self.__refresh_event_meta.get(event)

        if not event_meta:
            return False

        return event_meta.refresh_children

    def __parse_style_object_name(self, object_name: str):
        """
        Parses a shorthand object name string that includes dynamic properties.

        Args:
            object_name (str): Suffix following the pattern 'name[prop=val]'.
        """

        if object_name is None:
            return

        _logger.debug("Parsing composed style object name.")
        _logger.debug("raw=%s", object_name)
        match = re.compile(r"(\w+)?(\[.*?])?").match(object_name)
        style_object_name = match.group(1)
        properties_string = match.group(2)

        if style_object_name is not None:
            _logger.debug("style_object_name=%s", style_object_name)
            self.__object_name = style_object_name

        if properties_string is not None:
            properties_string = properties_string[1:-1]
            properties = properties_string.split(",")

            for prop in properties:
                name, value = prop.split("=")
                name = name.strip()
                value = value.strip()

                _logger.debug("%s=%s", name, value)
                self.__properties[name] = value

    @staticmethod
    def __parse_alignment(alignment: str) -> Qt.AlignmentFlag:
        """
        Converts a hyphen-separated alignment string into Qt AlignmentFlags.
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
        Converts a dictionary of CSS properties into a standard QSS string.
        """

        stylesheet_string = ""

        _logger.debug("Parsing stylesheet.")
        for key, value in stylesheet.items():
            stylesheet_string += f"{key}: {value};\n"

        _logger.debug("raw=%s, formatted=%s", stylesheet, stylesheet_string)
        return stylesheet_string
