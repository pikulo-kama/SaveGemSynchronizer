from typing import Final

from savegem.common.core.app_data import AppData
from savegem.common.core.holders import locales, prop
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class AppState(AppData):
    """
    Used to retrieve and operate with application dynamic state.
    e.g. locale or selected game.
    """

    AppStateTable: Final = "app_state"

    SelectedGame: Final = "current_game"
    SelectedLocale: Final = "language"
    IsAutoMode: Final = "is_auto_mode"
    WindowWidth: Final = "window_width"
    WindowHeight: Final = "window_height"

    def __init__(self):
        super().__init__()
        self.__table = db().table(self.AppStateTable)
        self.__table.retrieve()

        self.__on_state_change = None

    @property
    def game_name(self):
        """
        Get active game.
        """

        game_name = self.__table.get_first(self.SelectedGame)

        if game_name not in self._app.games.names:
            default_game = self._app.games.names[0]
            _logger.warning("Game '%s' was not found. Using game '%s' as default.", str(game_name), default_game)

            game_name = default_game
            self.game_name = default_game

        _logger.debug("Current game = %s", game_name)
        return game_name

    @game_name.setter
    def game_name(self, game_name: str):
        """
        Set game as active.
        """
        self.__set_state_value(self.SelectedGame, game_name, execute_callback=True)

    @property
    def locale(self):
        """
        Get active locale.
        """

        locale = self.__table.get_first(self.SelectedLocale)

        if locale not in locales():
            default_locale = prop("defaultLocale")
            _logger.warning("Locale '%s' was not found. Using default locale '%s'.", str(locale), default_locale)

            locale = default_locale
            self.locale = default_locale

        _logger.debug("Current locale = %s", locale)
        return locale

    @locale.setter
    def locale(self, locale: str):
        """
        Set active locale.
        """
        self.__set_state_value(self.SelectedLocale, locale, execute_callback=True)

    @property
    def is_auto_mode(self):
        """
        Used to check if auto download/upload mode is enabled.
        """
        return self.__table.get_first(self.IsAutoMode) == 1

    @is_auto_mode.setter
    def is_auto_mode(self, is_auto_mode):
        """
        Used to enable/disabled auto mode.
        """
        is_auto_mode = 1 if is_auto_mode else 0
        self.__set_state_value(self.IsAutoMode, is_auto_mode, execute_callback=True)

    @property
    def width(self):
        """
        Used to get window width.
        """
        return self.__table.get_first(self.WindowWidth) or prop("windowWidth")

    @width.setter
    def width(self, width: int):
        """
        Used to set window width.
        """
        self.__set_state_value(self.WindowWidth, width)

    @property
    def height(self):
        """
        Used to get window height.
        """
        return self.__table.get_first(self.WindowHeight) or prop("windowHeight")

    @height.setter
    def height(self, height: int):
        """
        Used to set window height.
        """
        self.__set_state_value(self.WindowHeight, height)

    def refresh(self):
        """
        Used to reload application state.
        """
        self.__table.retrieve()

    def on_change(self, callback):
        """
        Used to set callback that would run each time state is modified.
        """
        self.__on_state_change = callback

    def __set_state_value(self, property_name: str, value, execute_callback=False):
        """
        Wrapper to set state value.
        Will call on state change callback if defined.
        """

        self.__table.set_first(property_name, value)
        self.__table.save()

        if execute_callback and self.__on_state_change is not None:
            self.__on_state_change()
