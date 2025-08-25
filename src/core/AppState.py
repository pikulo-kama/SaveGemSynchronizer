from constants import STATE_SELECTED_GAME, STATE_SELECTED_LOCALE
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.util.file import resolve_app_data
from src.util.logger import get_logger


logger = get_logger(__name__)


class AppState:

    __state = EditableJsonConfigHolder(resolve_app_data("state"))

    @staticmethod
    def set_game(game_name: str):
        AppState.__state.set_value(STATE_SELECTED_GAME, game_name)

    @staticmethod
    def get_game(default_value: str = None):
        return AppState.__get_value(STATE_SELECTED_GAME, default_value)

    @staticmethod
    def set_locale(locale: str):
        AppState.__state.set_value(STATE_SELECTED_LOCALE, locale)

    @staticmethod
    def get_locale(default_value: str = None):
        return AppState.__get_value(STATE_SELECTED_LOCALE, default_value)

    @staticmethod
    def __get_value(key: str, default_value):
        state_value = AppState.__state.get_value(key)

        if state_value is None:
            logger.warn("Value for '%s' is missing in state. Using '%s' as default value.", key, default_value)
            AppState.__state.set_value(key, default_value)
            return default_value

        logger.debug("State value %s=%s", key, state_value)
        return state_value
