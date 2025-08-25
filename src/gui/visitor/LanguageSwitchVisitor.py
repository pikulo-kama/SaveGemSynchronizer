import tkinter as tk
from tkinter import font

from src.core.AppState import AppState
from src.core.TextResource import tr
from src.core.holders import prop, locales
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from src.util.logger import get_logger

logger = get_logger(__name__)


class LanguageSwitchVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_language_switch_control(gui)

    def is_enabled(self):
        # Only show control when there are multiple locales configured.
        return len(locales) > 1

    def refresh(self, gui: GUI):
        language_id = tr("languageId")

        logger.debug("Refreshing language switch (%s)", language_id)
        gui.language_button.configure(text=language_id)

    @staticmethod
    def __add_language_switch_control(gui: GUI):

        def switch_language():
            LanguageSwitchVisitor.__switch_language(gui)

        gui.language_button = tk.Button(
            gui.window,
            command=switch_language,
            font=("Small Fonts", 14, font.BOLD),
            bd=0,
            padx=3,
            cursor="hand2",
            bg=prop("secondaryButton")["colorStatic"],
            fg=prop("primaryColor")
        )

        gui.language_button.pack()
        gui.language_button.place(relx=.05, rely=.05, anchor=tk.N)

    @staticmethod
    def __switch_language(gui: GUI):

        current_locale = AppState.get_locale(prop("defaultLocale"))
        next_locale_index = locales.index(current_locale) + 1

        if next_locale_index == len(locales):
            next_locale_index = 0

        new_locale = locales[next_locale_index]

        logger.info("Language has been changed.")
        logger.info("Selected language - %s", new_locale)

        AppState.set_locale(new_locale)
        gui.refresh()
