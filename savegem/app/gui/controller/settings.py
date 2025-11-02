from PyQt6.QtWidgets import QWidget

from constants import TimeFormat, File
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.combobox import QCustomComboBox
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.window import gui
from savegem.common.core.context import app
from savegem.common.core.text_resource import tr
from savegem.common.db.manager import db
from savegem.common.util.file import delete_file, resolve_app_data


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
            app().state.locale = new_locale

            gui().refresh(UIRefreshEvent.LanguageChange)

        for language in db().table("setup_locale").retrieve():
            language_combobox.addItem(
                language.get("locale_name"),
                language.get("locale_id"),
            )

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
            app().state.time_format = time_format_id

        time_format_dropdown.addItem(tr("label_TimeFormat12"), TimeFormat.Regular)
        time_format_dropdown.addItem(tr("label_TimeFormat24"), TimeFormat.Military)

        time_format_dropdown.setCurrentIndex(app().state.time_format)
        time_format_dropdown.currentIndexChanged.connect(on_time_format_change)  # noqa

    def refresh(self, time_format_dropdown: QCustomComboBox):
        time_format_dropdown.setItemText(0, tr("label_TimeFormat12"))
        time_format_dropdown.setItemText(1, tr("label_TimeFormat24"))


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

            # Delete auth token.
            delete_file(resolve_app_data(File.GDriveToken))
            gui().destroy()
            exit(0)

        logout_button.clicked.connect(  # noqa
            lambda: confirmation(
                tr("confirmation_ConfirmLogout"),
                logout
            )
        )
