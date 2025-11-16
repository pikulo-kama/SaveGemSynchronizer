from typing import Final, Optional

from constants import TimeFormat
from savegem.common.core.app_data import AppData
from savegem.common.core.holders import locales, prop
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseTable
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
    TimeFormatId: Final = "time_format_id"
    ColorTheme: Final = "color_theme"

    TemporaryUser: Final = "<temporary>"

    def __init__(self, app):
        super().__init__(app)
        self.__state_table: Optional[DatabaseTable] = None
        self.__on_state_change = None

        self.refresh()

    @property
    def game_name(self):
        """
        Get active game.
        """

        game_name = self.__state_table.get_first(self.SelectedGame)

        if game_name not in self.app.games.names:
            default_game = self.app.games.names[0]
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

        locale = self.__state_table.get_first(self.SelectedLocale)

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
    def color_theme(self):
        """
        Used to get configured application color theme.
        """
        return self.__state_table.get_first(self.ColorTheme)

    @color_theme.setter
    def color_theme(self, color_theme: str):
        """
        Used to set application color theme.
        """
        self.__set_state_value(self.ColorTheme, color_theme)

    @property
    def time_format(self):
        """
        Used to get configured time format.

        0 - 12-hour format
        1 - 24-hour format
        """

        time_format = self.__state_table.get_first(self.TimeFormatId)

        if time_format is None:
            time_format = TimeFormat.Military

        return time_format

    @time_format.setter
    def time_format(self, time_format_id):
        """
        Used to set time format.
        """
        self.__set_state_value(self.TimeFormatId, time_format_id)

    def refresh(self):
        """
        Used to load user configuration from database.
        If configuration is missing then new one would be
        created.
        """

        user_id = self.TemporaryUser

        if self.app.users.current is not None:
            user_id = self.app.users.current.id

        # Remove temporary user record
        # in case it's already in database.
        db().table(self.AppStateTable) \
            .where("user_id = ?", self.TemporaryUser) \
            .retrieve() \
            .remove_all() \
            .save()

        state = db().table(self.AppStateTable) \
            .where("user_id = ?", user_id) \
            .retrieve()

        # Add row if no entry is
        # present for the user.
        if state.is_empty:
            state.add_row()
            state.set_first("user_id", user_id)

        self.__state_table = state

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

        self.__state_table.set_first(property_name, value)
        self.__state_table.save()

        if execute_callback and self.__on_state_change is not None:
            self.__on_state_change()
