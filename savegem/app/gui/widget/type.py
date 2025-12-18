import importlib
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)

_widget_type_pool: list["WidgetType"] = []
_layout_type_pool: list["UIObjectType"] = []


def _get_widget_type_pool():
    """
    Retrieves and caches the list of available widget types from the database.

    Returns:
        list[WidgetType]: A list of initialized WidgetType metadata objects.
    """

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
    Retrieves widget type metadata by its unique identifier.

    Args:
        widget_type_name (str): The name/ID of the widget type (e.g., 'button').

    Returns:
        WidgetType: The matching metadata object.
    """
    return next(widget_type for widget_type in _get_widget_type_pool() if widget_type.name == widget_type_name)


def get_layout_type(layout_type_name: str):
    """
    Retrieves layout type metadata by its unique identifier.

    Args:
        layout_type_name (str): The name/ID of the layout type (e.g., 'vertical').

    Returns:
        Optional[UIObjectType]: The matching layout metadata, or None if not found.
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
    Dynamically imports a module and retrieves a class attribute from it.

    Args:
        class_path (str): The dot-separated full path to the class.

    Returns:
        type: The resolved Python class object.
    """

    module_path, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)

    return getattr(module, class_name)


class UIObjectType:
    """
    A base container for UI-related class metadata.

    This class stores the actual Python class type and its associated
    identifier, allowing for dynamic instantiation of UI elements.
    """

    def __init__(self, widget_type_name: str, widget_class: type):
        """
        Initializes the UI object type with a name and class reference.
        """

        self.__widget_type = widget_class
        self.__widget_type_name = widget_type_name

    @property
    def type(self):
        """
        Returns the Python class reference.
        """
        return self.__widget_type

    @property
    def name(self):
        """
        Returns the identifier name of the object type.
        """
        return self.__widget_type_name


class WidgetType(UIObjectType):
    """
    Extended metadata for widget objects, including interaction state.
    """

    def __init__(self, widget_type_name: str, widget_class: type, is_interactable: bool):
        """
        Initializes the widget type with interaction metadata.
        """

        super().__init__(widget_type_name, widget_class)
        self.__is_interactable = is_interactable

    @property
    def is_interactable(self):
        """
        Checks if the widget type supports user interaction.
        """
        return self.__is_interactable
