import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from savegem.common.core import ApplicationContext


class AppData(abc.ABC):  # pragma: no cover
    """
    Represents root level context object.
    Has application context ap property.
    """

    def __init__(self):
        self._app: "ApplicationContext|None" = None

    def link(self, app: "ApplicationContext"):
        """
        Used to link application context to app data.
        """
        self._app = app

    @abc.abstractmethod
    def refresh(self):
        """
        Should be used to reinitialize app data.
        """
        pass
