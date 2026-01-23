import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.savegem.common.core.context import ApplicationContext


class AppData(abc.ABC):  # pragma: no cover
    """
    Represents root level context object.
    Has application context ap property.
    """

    def __init__(self, app: "ApplicationContext"):
        self.__app: "ApplicationContext|None" = app

    @property
    def app(self) -> "ApplicationContext":
        """
        Used to get application context linked
        to app data instance.
        """
        return self.__app

    def initialize(self):
        """
        Should be used for
        initial app data initialization.
        """
        pass

    @abc.abstractmethod
    def refresh(self):
        """
        Should be used to reinitialize app data.
        """
        pass
