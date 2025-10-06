from savegem.common.core.game_config import Game


class MockGame(Game):

    def __init__(self, name, process_name, auto_mode_allowed, metadata=None):  # noqa
        self._name = name
        self._process_name = process_name
        self._auto_mode_allowed = auto_mode_allowed
        self._metadata = metadata
