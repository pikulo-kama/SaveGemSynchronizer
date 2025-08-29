from typing import Final

from src.core.app_data import AppData
from src.core.editable_json_config_holder import EditableJsonConfigHolder
from src.core.holders import locales, prop
from src.util.file import resolve_app_data
from src.util.logger import get_logger


_logger = get_logger(__name__)

_STATE_SELECTED_GAME: Final = "game"
_STATE_SELECTED_LOCALE: Final = "locale"


class _AppState(AppData):
    """
    Used to retrieve and operate with application dynamic state.
    e.g. locale or selected game.
    """

    def __init__(self):
        super().__init__()
        self.__state = EditableJsonConfigHolder(resolve_app_data("state"))
        # This shouldn't be part of state since it would be a security issue.
        self.__user_email = None

    @property
    def user_email(self):
        """
        Used to get email address of currently authenticated user.
        """
        return self.__user_email

    @user_email.setter
    def user_email(self, user_email: str):
        """
        Used to set email of currently authenticated user in memory.
        This will not be written to state.json.
        """
        self.__user_email = user_email

    @property
    def game_name(self):
        """
        Get active game.
        """

        game_name = self.__state.get_value(_STATE_SELECTED_GAME)

        if game_name not in self._app.games.names:
            default_game = self._app.games.names[0]
            _logger.warn("Game '%s' was not found. Using game '%s' as default.", str(game_name), default_game)

            game_name = default_game
            self.game_name = default_game

        _logger.debug("Current game = %s", game_name)
        return game_name

    @game_name.setter
    def game_name(self, game_name: str):
        """
        Set game as active.
        """
        self.__state.set_value(_STATE_SELECTED_GAME, game_name)

    @property
    def locale(self):
        """
        Get active locale.
        """

        locale = self.__state.get_value(_STATE_SELECTED_LOCALE)

        if locale not in locales:
            default_locale = prop("defaultLocale")
            _logger.warn("Locale '%s' was not found. Using default locale '%s'.", str(locale), default_locale)

            locale = default_locale
            self.locale = default_locale

        _logger.debug("Current locale = %s", locale)
        return locale

    @locale.setter
    def locale(self, locale: str):
        """
        Set active locale.
        """
        self.__state.set_value(_STATE_SELECTED_LOCALE, locale)
