from src.core.app_config import _AppConfig
from src.core.app_state import _AppState
from src.core.game_config import _GameConfig
from src.core.user import _UserState


class _ApplicationContext:
    """
    Contains all runtime information. Has:
    - Allows control over state (locale, selected game)
    - Has list of loaded games and their properties
    - Allows to get and update save versioning
    """

    def __init__(self):
        self.__state = _AppState()
        self.__app_config = _AppConfig()
        self.__game_config = _GameConfig()
        self.__user_state = _UserState()

        self.__state.link(self)
        self.__app_config.link(self)
        self.__game_config.link(self)
        self.__user_state.link(self)

    @property
    def state(self) -> _AppState:
        """
        Application state
        """
        return self.__state

    @property
    def games(self) -> _GameConfig:
        """
        Available games' configurations.
        """
        return self.__game_config

    @property
    def user(self) -> _UserState:
        """
        Information about authenticated user.
        """
        return self.__user_state

    @property
    def config(self) -> _AppConfig:
        """
        Application configurations.
        """
        return self.__app_config


app = _ApplicationContext()
