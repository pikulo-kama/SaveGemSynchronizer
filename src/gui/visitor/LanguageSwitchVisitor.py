import tkinter as tk

from src.core.AppState import AppState
from src.core.TextResource import tr
from src.core.holders import prop, locales
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor


class LanguageSwitchVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_language_switch_control(gui)

    def is_enabled(self):
        # Only show control when there are multiple locales configured.
        return len(locales) > 1

    def refresh(self, gui: GUI):
        gui.language_button.configure(text=tr("languageId"))

    @staticmethod
    def __add_language_switch_control(gui: GUI):

        def switch_language():
            LanguageSwitchVisitor.__switch_language(gui)

        gui.language_button = tk.Button(
            gui.window,
            command=switch_language,
            font=("Segoe UI Emoji", 14),
            bd=0,
            padx=3,
            cursor="hand2",
            bg=prop("secondaryButton")["colorStatic"]
        )

        gui.language_button.pack()
        gui.language_button.place(relx=.05, rely=.05, anchor=tk.N)

    @staticmethod
    def __switch_language(gui: GUI):

        current_locale = AppState.get_locale(prop("defaultLocale"))
        next_locale_index = locales.index(current_locale) + 1

        if next_locale_index == len(locales):
            next_locale_index = 0

        AppState.set_locale(locales[next_locale_index])
        gui.refresh()
