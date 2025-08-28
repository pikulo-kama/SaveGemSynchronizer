from constants import STATE_SELECTED_GAME, STATE_SELECTED_LOCALE
from src.core.editable_json_config_holder import EditableJsonConfigHolder
from src.util.file import resolve_app_data
from src.util.logger import get_logger


logger = get_logger(__name__)


class AppState:
    """
    Used to retrieve and operate with application dynamic state.
    e.g. locale or selected game.
    """

    __state = EditableJsonConfigHolder(resolve_app_data("state"))
    # This shouldn't be part of state since it would be a security issue.
    __user_email: str = None

    @classmethod
    def set_user_email(cls, user_email: str):
        """
        Used to set email of currently authenticated user in memory.
        This will not be written to state.json.
        """
        cls.__user_email = user_email

    @classmethod
    def get_user_email(cls):
        """
        Used to get email address of currently authenticated user.
        """
        return cls.__user_email

    @classmethod
    def set_game(cls, game_name: str):
        """
        Set game as active.
        """
        cls.__state.set_value(STATE_SELECTED_GAME, game_name)

    @classmethod
    def get_game(cls, default_value: str = None):
        """
        Get active game.
        """
        return cls.__get_value(STATE_SELECTED_GAME, default_value)

    @classmethod
    def set_locale(cls, locale: str):
        """
        Set active locale.
        """
        cls.__state.set_value(STATE_SELECTED_LOCALE, locale)

    @classmethod
    def get_locale(cls, default_value: str = None):
        """
        Get active locale.
        """
        return cls.__get_value(STATE_SELECTED_LOCALE, default_value)

    @classmethod
    def __get_value(cls, key: str, default_value):
        """
        For internal use.
        Used to get value from state, if value is not in state
        then it would be populated with default one and persisted.
        """
        state_value = cls.__state.get_value(key)

        if state_value is None:
            logger.warn("Value for '%s' is missing in state. Using '%s' as default value.", key, default_value)
            cls.__state.set_value(key, default_value)
            return default_value

        logger.debug("State value %s=%s", key, state_value)
        return state_value
