import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from savegem.common.core.context import ApplicationContext


class AppData(abc.ABC):  # pragma: no cover
    """
    Represents root level context object.
    Has application context ap property.
    """

    def __init__(self, app: "ApplicationContext"):
        self.__app: "ApplicationContext|None" = app
        app.link(self)

    def link(self, app: "ApplicationContext"):
        """
        Used to link application context to app data.
        """
        self.__app = app

    @property
    def app(self) -> "ApplicationContext":
        """
        Used to get application context linked
        to app data instance.
        """
        return self.__app

    def initialize(self):
        pass

    @abc.abstractmethod
    def refresh(self):
        """
        Should be used to reinitialize app data.
        """
        pass
