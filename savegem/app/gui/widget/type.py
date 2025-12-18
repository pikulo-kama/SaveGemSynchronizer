import importlib
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)

_widget_type_pool: list["WidgetType"] = []
_layout_type_pool: list["UIObjectType"] = []


def _get_widget_type_pool():
    global _widget_type_pool

    if len(_widget_type_pool) == 0:

        widget_types = db().retrieve_table("setup_widget_type")

        for widget_type in widget_types:
            type_name = widget_type.get("widget_type_id")
            class_path = get_class_from_path(widget_type.get("class_path"))
            is_interactable = widget_type.get("is_interactable") == 1

            _logger.debug("Adding %s to widget type pool.", class_path)
            _widget_type_pool.append(WidgetType(type_name, class_path, is_interactable))

    return _widget_type_pool


def get_widget_type(widget_type_name: str):
    """
    Used to get widget type metadata by the name.
    """
    return next(widget_type for widget_type in _get_widget_type_pool() if widget_type.name == widget_type_name)


def get_layout_type(layout_type_name: str):
    """
    Used to get layout type metadata by the name.
    """

    global _layout_type_pool

    if len(_layout_type_pool) == 0:

        layout_types = db().retrieve_table("setup_layout_type")

        for layout_type in layout_types:
            type_name = layout_type.get("layout_type_id")
            class_path = get_class_from_path(layout_type.get("class_path"))

            _logger.debug("Adding %s to layout type pool.", class_path)
            _layout_type_pool.append(UIObjectType(type_name, class_path))

    return next((layout_type for layout_type in _layout_type_pool if layout_type.name == layout_type_name), None)


def get_class_from_path(class_path: str):
    """
    Dynamically loads and returns a class object given its fully qualified path string.
    """

    module_path, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)

    return getattr(module, class_name)


class UIObjectType:
    """
    Represents type-object metadata.
    """

    def __init__(self, widget_type_name: str, widget_class: type):
        self.__widget_type = widget_class
        self.__widget_type_name = widget_type_name

    @property
    def type(self):
        return self.__widget_type

    @property
    def name(self):
        return self.__widget_type_name


class WidgetType(UIObjectType):
    """
    Represents widget type object metadata.
    Has additional is_interactable property.
    """

    def __init__(self, widget_type_name: str, widget_class: type, is_interactable: bool):
        super().__init__(widget_type_name, widget_class)
        self.__is_interactable = is_interactable

    @property
    def is_interactable(self):
        return self.__is_interactable
