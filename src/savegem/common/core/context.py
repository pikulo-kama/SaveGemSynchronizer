from typing import Optional

from savegem.common.core.activity import Activity
from savegem.common.core.app_config import AppConfig
from savegem.common.core.app_state import AppState
from savegem.common.core.game_config import GameConfig
from savegem.common.core.settings import AppSettings
from savegem.common.core.user import UserState


_app: Optional["ApplicationContext"] = None


class ApplicationContext:
    """
    Contains all runtime app information. Provides:
    - Control over user app state (locale, selected game, etc.)
    - List of loaded games and their properties
    - Possibility to get and update save versioning
    - Possibility to work with activity data
    - Possibility to access game players data
    """

    def __init__(self):
        self.__user_state = UserState(self)
        self.__state = AppState(self)
        self.__app_config = AppConfig(self)
        self.__app_settings = AppSettings(self)
        self.__game_config = GameConfig(self)
        self.__activity = Activity(self)

    @property
    def state(self) -> AppState:
        """
        Application state
        """
        return self.__state

    @property
    def games(self) -> GameConfig:
        """
        Available games' configurations.
        """
        return self.__game_config

    @property
    def users(self) -> UserState:
        """
        Information about authenticated user.
        """
        return self.__user_state

    @property
    def config(self) -> AppConfig:
        """
        Application configurations.
        """
        return self.__app_config

    @property
    def settings(self) -> AppSettings:
        return self.__app_settings

    @property
    def activity(self) -> Activity:
        """
        Selected game activity data.
        """
        return self.__activity


def context():  # pragma: no cover
    """
    Used to get global app context instance.
    """

    global _app

    if _app is None:
        _app = ApplicationContext()

    return _app
