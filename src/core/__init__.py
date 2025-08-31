from src.core.app_state import _AppState
from src.core.game_config import _GameConfig
from src.core.last_save_info_config import _LastSaveInfoConfig
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
        self.__game_config = _GameConfig()
        self.__last_save_info = _LastSaveInfoConfig()
        self.__user_state = _UserState()

        self.__state.link(self)
        self.__game_config.link(self)
        self.__last_save_info.link(self)

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
    def last_save(self) -> _LastSaveInfoConfig:
        """
        Last save uploaded/downloaded save information.
        """
        return self.__last_save_info

    @property
    def user(self) -> _UserState:
        """
        Information about authenticated user.
        """
        return self.__user_state


app = _ApplicationContext()
