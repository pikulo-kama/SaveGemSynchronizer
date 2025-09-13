from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class AppData:
    """
    Represents root level context object.
    Has application context ap property.
    """

    def __init__(self):
        self._app: "_ApplicationContext|None" = None

    def link(self, app: "_ApplicationContext"):
        """
        Used to link application context to app data.
        """
        self._app = app
