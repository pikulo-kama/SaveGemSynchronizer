from typing import Final

from constants import File
from savegem.common.core.app_data import AppData
from savegem.common.core.editable_json_config_holder import EditableJsonConfigHolder
from savegem.common.core.holders import locales, prop
from savegem.common.util.file import resolve_app_data
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class _AppState(AppData):
    """
    Used to retrieve and operate with application dynamic state.
    e.g. locale or selected game.
    """

    __STATE_SELECTED_GAME: Final = "game"
    __STATE_SELECTED_LOCALE: Final = "locale"
    __STATE_IS_AUTO_MODE: Final = "isAutoMode"

    def __init__(self):
        super().__init__()
        self.__state = EditableJsonConfigHolder(resolve_app_data(File.AppState))
        self.__on_state_change = None

    @property
    def game_name(self):
        """
        Get active game.
        """

        game_name = self.__state.get_value(self.__STATE_SELECTED_GAME)

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
        self.__set_state_value(self.__STATE_SELECTED_GAME, game_name)

    @property
    def locale(self):
        """
        Get active locale.
        """

        locale = self.__state.get_value(self.__STATE_SELECTED_LOCALE)

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
        self.__set_state_value(self.__STATE_SELECTED_LOCALE, locale)

    @property
    def is_auto_mode(self):
        """
        Used to check if auto download/upload mode is enabled.
        """
        return self.__state.get_value(self.__STATE_IS_AUTO_MODE, False)

    @is_auto_mode.setter
    def is_auto_mode(self, is_auto_mode):
        """
        Used to enable/disabled auto mode.
        """
        self.__set_state_value(self.__STATE_IS_AUTO_MODE, is_auto_mode)

    def reload(self):
        self.__state = EditableJsonConfigHolder(resolve_app_data(File.AppState))

    def on_change(self, callback):
        """
        Used to set callback that would run each time state is modified.
        """
        self.__on_state_change = callback

    def __set_state_value(self, property_name: str, value):
        """
        Wrapper to set state value.
        Will call on state change callback if defined.
        """

        self.__state.set_value(property_name, value)

        if self.__on_state_change is not None:
            self.__on_state_change()
