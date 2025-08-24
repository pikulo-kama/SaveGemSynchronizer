from constants import STATE_SELECTED_GAME, STATE_SELECTED_LOCALE
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder


class AppState:

    __state = EditableJsonConfigHolder("state")

    @staticmethod
    def set_game(game_name: str):
        AppState.__set_value(STATE_SELECTED_GAME, game_name)

    @staticmethod
    def get_game(default_value: str):
        return AppState.__get_value(STATE_SELECTED_GAME, default_value)

    @staticmethod
    def set_locale(locale: str):
        AppState.__set_value(STATE_SELECTED_LOCALE, locale)

    @staticmethod
    def get_locale(default_value: str):
        return AppState.__get_value(STATE_SELECTED_LOCALE, default_value)

    @staticmethod
    def __get_value(key: str, default_value):
        state_value = AppState.__state.get_value(key)

        if state_value is None:
            AppState.__set_value(key, default_value)
            return default_value

        return state_value

    @staticmethod
    def __set_value(key: str, value: any):
        AppState.__state.set_value(key, value)
        AppState.__state.save()
