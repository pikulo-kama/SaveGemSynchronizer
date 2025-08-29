from src.core.app_state import _AppState
from src.core.game_config import _GameConfig
from src.core.last_save_info_config import _LastSaveInfoConfig


class _ApplicationContext:
    """
    Contains all runtime information. Has:
    - Allows control over state (locale, selected game)
    - Has list of loaded games and their properties
    - Allows to get and update save versioning
    """

    def __init__(self):
        self._state = _AppState()
        self._game_config = _GameConfig()
        self._last_save_info = _LastSaveInfoConfig()

        self._state.link(self)
        self._game_config.link(self)
        self._last_save_info.link(self)

    @property
    def state(self) -> _AppState:
        """
        Application state
        """
        return self._state

    @property
    def games(self) -> _GameConfig:
        """
        Available games' configurations.
        """
        return self._game_config

    @property
    def last_save(self) -> _LastSaveInfoConfig:
        """
        Last save uploaded/downloaded save information.
        """
        return self._last_save_info


app = _ApplicationContext()
