from constants import TimeFormat, File
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.combobox import QCustomComboBox
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.style import ColorMode
from savegem.app.gui.window import gui
from savegem.common.core.context import app
from savegem.common.core.text_resource import tr
from savegem.common.db.manager import db
from savegem.common.util.file import delete_file, resolve_app_data
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class LanguageDropdownController(WidgetController):
    """
    Used to control language dropdown setting.
    """

    def setup(self, language_combobox: QCustomComboBox):

        def on_language_change(index: int):
            """
            Callback which is called when language selection in
            dropdown changes.
            """

            new_locale = language_combobox.itemData(index)

            _logger.debug("Changing language to %s", new_locale)
            app().state.locale = new_locale
            gui().refresh(UIRefreshEvent.LanguageChange)

        for language in db().retrieve_table("setup_locale"):
            locale_id = language.get("locale_id")
            locale_name = language.get("locale_name")

            _logger.info("Adding language with code %s to language dropdown.", locale_id)
            language_combobox.addItem(locale_name, locale_id)

        target_language_id = language_combobox.findData(app().state.locale)
        language_combobox.setCurrentIndex(target_language_id)
        language_combobox.currentIndexChanged.connect(on_language_change)  # noqa


class TimeFormatDropdownController(WidgetController):
    """
    Used to control time format dropdown setting.
    """

    def setup(self, time_format_dropdown: QCustomComboBox):

        def on_time_format_change(index: int):
            """
            Callback executed when time format dropdown
            selection changes.
            """

            time_format_id = time_format_dropdown.itemData(index)

            _logger.debug("Changing time format to %s", time_format_id)
            app().state.time_format = time_format_id

        time_format_dropdown.addItem(tr("label_TimeFormat12"), TimeFormat.Regular)
        time_format_dropdown.addItem(tr("label_TimeFormat24"), TimeFormat.Military)

        time_format_dropdown.setCurrentIndex(app().state.time_format)
        time_format_dropdown.currentIndexChanged.connect(on_time_format_change)  # noqa

    def refresh(self, time_format_dropdown: QCustomComboBox):
        time_format_dropdown.setItemText(0, tr("label_TimeFormat12"))
        time_format_dropdown.setItemText(1, tr("label_TimeFormat24"))


class ColorThemeDropdownController(WidgetController):
    """
    Used to control dropdown with application color modes.
    """

    def setup(self, theme_dropdown: QCustomComboBox):

        def on_theme_change(index: int):
            color_theme = theme_dropdown.itemData(index)

            _logger.debug("Changing color theme to %s", color_theme)
            app().state.color_theme = color_theme
            gui().reload_styles()
            self.manager.refresh()

        theme_dropdown.addItem(tr("label_ColorModeSystem"), None)
        theme_dropdown.addItem(tr("label_ColorModeLight"), ColorMode.Light)
        theme_dropdown.addItem(tr("label_ColorModeDark"), ColorMode.Dark)

        current_theme_index = theme_dropdown.findData(app().state.color_theme)
        theme_dropdown.setCurrentIndex(current_theme_index)
        theme_dropdown.currentIndexChanged.connect(on_theme_change)  # noqa

    def refresh(self, theme_dropdown: QCustomComboBox):
        theme_dropdown.setItemText(0, tr("label_ColorModeSystem"))
        theme_dropdown.setItemText(1, tr("label_ColorModeLight"))
        theme_dropdown.setItemText(2, tr("label_ColorModeDark"))


class LogoutController(WidgetController):
    """
    Used to control 'Log Out' button.
    """

    def setup(self, logout_button: QCustomPushButton):

        def logout():
            """
            Callback function that is being called
            when logout button is clicked.
            """

            _logger.debug("Logging out from application.")

            # Delete auth token.
            delete_file(resolve_app_data(File.GDriveToken))
            gui().destroy()

            exit(0)

        logout_button.clicked.connect(  # noqa
            lambda: gui().confirmation(
                tr("confirmation_ConfirmLogout"),
                logout
            )
        )
