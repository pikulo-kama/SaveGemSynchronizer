from constants import STATE_SELECTED_GAME, STATE_SELECTED_LOCALE
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.util.file import resolve_app_data
from src.util.logger import get_logger


logger = get_logger(__name__)


class AppState:
    """
    Used to retrieve and operate with application dynamic state.
    e.g. locale or selected game.
    """

    __state = EditableJsonConfigHolder(resolve_app_data("state"))

    @staticmethod
    def set_game(game_name: str):
        """
        Set game as active.
        """
        AppState.__state.set_value(STATE_SELECTED_GAME, game_name)

    @staticmethod
    def get_game(default_value: str = None):
        """
        Get active game.
        """
        return AppState.__get_value(STATE_SELECTED_GAME, default_value)

    @staticmethod
    def set_locale(locale: str):
        """
        Set active locale.
        """
        AppState.__state.set_value(STATE_SELECTED_LOCALE, locale)

    @staticmethod
    def get_locale(default_value: str = None):
        """
        Get active locale.
        """
        return AppState.__get_value(STATE_SELECTED_LOCALE, default_value)

    @staticmethod
    def __get_value(key: str, default_value):
        """
        For internal use.
        Used to get value from state, if value is not in state
        then it would be populated with default one and persisted.
        """
        state_value = AppState.__state.get_value(key)

        if state_value is None:
            logger.warn("Value for '%s' is missing in state. Using '%s' as default value.", key, default_value)
            AppState.__state.set_value(key, default_value)
            return default_value

        logger.debug("State value %s=%s", key, state_value)
        return state_value
