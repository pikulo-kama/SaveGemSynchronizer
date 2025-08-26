import tkinter as tk
from tkinter import ttk

from src.core.AppState import AppState
from src.core.TextResource import tr
from src.core.holders import prop, locales
from src.gui.gui import GUI
from src.gui.style import add_button_movement_effect
from src.gui.visitor.Visitor import Visitor
from src.util.logger import get_logger

logger = get_logger(__name__)


class LanguageSwitchVisitor(Visitor):
    """
    Used to render language switch button.
    Enabled only if there are at least two languages configured.
    """

    def __init__(self):
        self.__language_switch = None

    def visit(self, gui: GUI):
        self.__add_language_switch_control(gui)

    def is_enabled(self):
        # Only show control when there are multiple locales configured.
        return len(locales) > 1

    def refresh(self, gui: GUI):
        language_id = tr("languageId")

        # Limit language code to 2 characters.
        if len(language_id) > 2:
            language_id = language_id[:2]

        logger.debug("Refreshing language switch (%s)", language_id)
        self.__language_switch.configure(text=language_id)

    def __add_language_switch_control(self, gui: GUI):
        """
        Used to render language switch control.
        """

        self.__language_switch = ttk.Button(
            gui.window(),
            command=lambda: LanguageSwitchVisitor.__switch_language(gui),
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

        current_locale = AppState.get_locale(prop("defaultLocale"))
        next_locale_index = locales.index(current_locale) + 1

        if next_locale_index == len(locales):
            next_locale_index = 0

        new_locale = locales[next_locale_index]

        logger.info("Language has been changed.")
        logger.info("Selected language - %s", new_locale)

        AppState.set_locale(new_locale)
        gui.refresh()
