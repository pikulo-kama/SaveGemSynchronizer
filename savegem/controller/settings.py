import sys

from kui.component.button import KamaPushButton
from kui.component.combobox import KamaComboBox
from kui.core.app import KamaApplication
from kui.core.controller import WidgetController
from kui.core.style import ColorMode
from kui_db_plugin.database import db
from kutil.file import delete_file
from kutil.logger import get_logger

from savegem.constants import TimeFormat, File, UIRefreshEvent
from savegem.common.core.context import context

_logger = get_logger(__name__)


class LanguageDropdownController(WidgetController):
    """
    Used to control language dropdown setting.
    """

    def setup(self, language_combobox: KamaComboBox):

        def on_language_change(index: int):
            """
            Callback which is called when language selection in
            dropdown changes.
            """

            application = KamaApplication()
            new_locale = language_combobox.itemData(index)

            _logger.debug("Changing language to %s", new_locale)
            context().state.locale = new_locale
            application.window.refresh(UIRefreshEvent.LanguageChange)

        for language in db.retrieve_table("setup_locale"):
            locale_id = language.get("locale_id")
            locale_name = language.get("locale_name")

            _logger.info("Adding language with code %s to language dropdown.", locale_id)
            language_combobox.addItem(locale_name, locale_id)

        target_language_id = language_combobox.findData(context().state.locale)
        language_combobox.setCurrentIndex(target_language_id)
        language_combobox.currentIndexChanged.connect(on_language_change)  # noqa


class TimeFormatDropdownController(WidgetController):
    """
    Used to control time format dropdown setting.
    """

    def setup(self, time_format_dropdown: KamaComboBox):

        def on_time_format_change(index: int):
            """
            Callback executed when time format dropdown
            selection changes.
            """

            time_format_id = time_format_dropdown.itemData(index)

            _logger.debug("Changing time format to %s", time_format_id)
            context().state.time_format = time_format_id

        application = KamaApplication()
        time_format_dropdown.addItem(application.tr("label_TimeFormat12"), TimeFormat.Regular)
        time_format_dropdown.addItem(application.tr("label_TimeFormat24"), TimeFormat.Military)

        time_format_dropdown.setCurrentIndex(context().state.time_format)
        time_format_dropdown.currentIndexChanged.connect(on_time_format_change)  # noqa

    def refresh(self, time_format_dropdown: KamaComboBox):
        application = KamaApplication()
        time_format_dropdown.setItemText(0, application.tr("label_TimeFormat12"))
        time_format_dropdown.setItemText(1, application.tr("label_TimeFormat24"))


class ColorThemeDropdownController(WidgetController):
    """
    Used to control dropdown with application color modes.
    """

    def setup(self, theme_dropdown: KamaComboBox):
        application = KamaApplication()

        def on_theme_change(index: int):
            color_theme = theme_dropdown.itemData(index)

            _logger.debug("Changing color theme to %s", color_theme)
            context().state.color_theme = color_theme
            application.window.reload_styles()
            self.manager.refresh()

        theme_dropdown.addItem(application.tr("label_ColorModeSystem"), None)
        theme_dropdown.addItem(application.tr("label_ColorModeLight"), ColorMode.Light)
        theme_dropdown.addItem(application.tr("label_ColorModeDark"), ColorMode.Dark)

        current_theme_index = theme_dropdown.findData(context().state.color_theme)
        theme_dropdown.setCurrentIndex(current_theme_index)
        theme_dropdown.currentIndexChanged.connect(on_theme_change)  # noqa

    def refresh(self, theme_dropdown: KamaComboBox):
        application = KamaApplication()
        theme_dropdown.setItemText(0, application.tr("label_ColorModeSystem"))
        theme_dropdown.setItemText(1, application.tr("label_ColorModeLight"))
        theme_dropdown.setItemText(2, application.tr("label_ColorModeDark"))


class LogoutController(WidgetController):
    """
    Used to control 'Log Out' button.
    """

    def setup(self, logout_button: KamaPushButton):
        application = KamaApplication()

        def logout():
            """
            Callback function that is being called
            when logout button is clicked.
            """

            _logger.debug("Logging out from application.")

            # Delete auth token.
            delete_file(application.discovery.get_app_data_root(File.GDriveToken))
            application.window.destroy()

            sys.exit(0)

        logout_button.clicked.connect(  # noqa
            lambda: application.window.confirmation(
                application.tr("confirmation_ConfirmLogout"),
                logout
            )
        )
