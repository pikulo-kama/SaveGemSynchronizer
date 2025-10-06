from savegem.common.core.activity import Activity
from savegem.common.core.app_config import AppConfig
from savegem.common.core.app_data import AppData
from savegem.common.core.app_state import AppState
from savegem.common.core.game_config import GameConfig
from savegem.common.core.user import UserState


class ApplicationContext:
    """
    Contains all runtime information. Provides:
    - Control over state (locale, selected game)
    - List of loaded games and their properties
    - Possibility to get and update save versioning
    - Possibility to work with activity data
    - Possibility to access current user data
    """

    def __init__(self):

        self.__linked_entities: list[AppData] = []

        self.__state = AppState()
        self.__app_config = AppConfig()
        self.__game_config = GameConfig()
        self.__user_state = UserState()
        self.__activity = Activity()

        self.__link(self.__state)
        self.__link(self.__app_config)
        self.__link(self.__game_config)
        self.__link(self.__user_state)
        self.__link(self.__activity)

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
    def user(self) -> UserState:
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
    def activity(self) -> Activity:
        """
        Selected game activity data.
        """
        return self.__activity

    def __link(self, entity: AppData):
        """
        Used to link app data instance to
        main application context.
        """

        entity.link(self)
        self.__linked_entities.append(entity)

    def refresh(self):
        """
        Used to refresh all application data.
        """

        for entity in self.__linked_entities:
            entity.refresh()


app = ApplicationContext()
