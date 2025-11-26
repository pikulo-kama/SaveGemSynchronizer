from savegem.common.core.game_config import Game, GameSettings


class MockGameSettings(GameSettings):

    def __init__(self, auto_mode: bool):  # noqa
        self.__auto_mode = auto_mode

    @property
    def auto_mode(self):
        return self.__auto_mode


class MockGame(Game):

    def __init__(self, name, process_name, auto_mode_allowed, settings: MockGameSettings = None, metadata=None):  # noqa
        self._name = name
        self._process_name = process_name
        self._auto_mode_allowed = auto_mode_allowed
        self._metadata = metadata
        self._settings = settings
