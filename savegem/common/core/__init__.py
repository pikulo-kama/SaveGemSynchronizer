from savegem.common.core.app_config import _AppConfig
from savegem.common.core.app_data import AppData
from savegem.common.core.app_state import _AppState
from savegem.common.core.game_config import _GameConfig
from savegem.common.core.user import _UserState


class _ApplicationContext:
    """
    Contains all runtime information. Has:
    - Allows control over state (locale, selected game)
    - Has list of loaded games and their properties
    - Allows to get and update save versioning
    """

    def __init__(self):

        self.__linked_entities: list[AppData] = []

        self.__state = _AppState()
        self.__app_config = _AppConfig()
        self.__game_config = _GameConfig()
        self.__user_state = _UserState()

        self.__link(self.__state)
        self.__link(self.__app_config)
        self.__link(self.__game_config)
        self.__link(self.__user_state)

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

    def __link(self, entity: AppData):
        entity.link(self)
        self.__linked_entities.append(entity)

    def reload(self):
        for entity in self.__linked_entities:
            entity.reload()


app = _ApplicationContext()
