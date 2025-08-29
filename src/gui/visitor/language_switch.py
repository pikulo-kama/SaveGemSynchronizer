import tkinter as tk

from src.core import app
from src.core.text_resource import tr
from src.core.holders import locales
from src.gui import GUI
from src.gui.component.wait_button import WaitButton
from src.gui.style import add_button_movement_effect
from src.gui.visitor import Visitor
from src.util.logger import get_logger
from src.util.thread import execute_in_thread

_logger = get_logger(__name__)


class LanguageSwitchVisitor(Visitor):
    """
    Used to render language switch button.
    Enabled only if there are at least two languages configured.
    """

    def __init__(self):
        self.__language_switch = None

    def visit(self, gui: GUI):
        self.__add_language_switch_control(gui)

    def refresh(self, gui: GUI):
        language_id = tr("languageId")

        # Limit language code to 2 characters.
        if len(language_id) > 2:
            language_id = language_id[:2]

        _logger.debug("Refreshing language switch (%s)", language_id)
        self.__language_switch.configure(text=language_id)

    def is_enabled(self):
        # Only show control when there are multiple locales configured.
        return len(locales) > 1

    def __add_language_switch_control(self, gui: GUI):
        """
        Used to render language switch control.
        """

        def switch_language():
            LanguageSwitchVisitor.__switch_language(gui)

        self.__language_switch = WaitButton(
            gui.window(),
            command=lambda: execute_in_thread(switch_language),
            cursor="hand2",
            style="SquareSecondary.16.TButton",
            takefocus=False
        )

        add_button_movement_effect(self.__language_switch)

        self.__language_switch.pack()
        self.__language_switch.place(relx=.05, rely=.13, anchor=tk.N)

    @staticmethod
    def __switch_language(gui: GUI):
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
        gui.refresh()
