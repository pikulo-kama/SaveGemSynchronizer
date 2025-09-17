from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.common.core.holders import locales
from savegem.app.gui.window import _GUI
from savegem.app.gui.component.wait_button import WaitButton
from savegem.app.gui.constants import TkState, TkCursor, UIRefreshEvent
from savegem.app.gui.visitor import Visitor
from savegem.common.util.logger import get_logger
from savegem.common.util.thread import execute_in_blocking_thread

_logger = get_logger(__name__)


class LanguageSwitchVisitor(Visitor):
    """
    Used to render language switch button.
    Enabled only if there are at least two languages configured.
    """

    def __init__(self):
        super().__init__(UIRefreshEvent.LanguageChange)
        self.__language_switch = None

    def visit(self, gui: _GUI):
        self.__add_language_switch_control(gui)

    def refresh(self, gui: _GUI):
        language_id = tr("languageId")

        # Limit language code to 2 characters.
        if len(language_id) > 2:
            language_id = language_id[:2]

        _logger.debug("Refreshing language switch (%s)", language_id)
        self.__language_switch.configure(text=language_id)

    def enable(self, gui: "_GUI"):
        self.__language_switch.configure(state=TkState.Default, cursor=TkCursor.Hand)

    def disable(self, gui: "_GUI"):
        self.__language_switch.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def is_enabled(self):
        # Only show control when there are multiple locales configured.
        return len(locales) > 1

    def __add_language_switch_control(self, gui: _GUI):
        """
        Used to render language switch control.
        """

        self.__language_switch = WaitButton(
            gui.top_left,
            command=lambda: execute_in_blocking_thread(lambda: self.__next_language(gui)),
            style="SquareSecondary.18.TButton"
        )

        self.__language_switch.grid(row=1, column=0, padx=(20, 0), pady=(10, 0))
        _logger.debug("Locale list - %s", locales)

    @staticmethod
    def __next_language(gui: _GUI):
        """
        Used as callback function when language switch button is being clicked.
        """

        next_locale_index = locales.index(app.state.locale) + 1

        if next_locale_index == len(locales):
            next_locale_index = 0

        new_locale = locales[next_locale_index]

        _logger.info("Language has been changed.")
        _logger.info("Selected language - %s", new_locale)

        app.state.locale = new_locale
        gui.refresh(UIRefreshEvent.LanguageChange)
