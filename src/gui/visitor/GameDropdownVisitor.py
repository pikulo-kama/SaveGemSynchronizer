from constants import EVENT_GAME_SELECTION_CHANGED
from src.core.AppState import AppState
from src.core.holders import games, prop
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from tkinter import ttk
import tkinter as tk


class GameDropdownVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_game_selection_dropdown(gui)

    def is_enabled(self):
        # Visitor should be enabled always even if there is one game, so it would still be obvious what game.
        # is selected.
        if len(games()) == 0:
            raise RuntimeError("There are no games configured in config/games.json. Can't proceed.")

        return True

    @staticmethod
    def __add_game_selection_dropdown(gui: GUI):
        game_names = [game["name"] for game in games()]
        combobox_state = "disabled" if len(game_names) == 1 else "normal"
        selected_game = AppState.get_game(game_names[0])
        print(selected_game)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=prop("secondaryButton")["colorHover"],
            foreground=prop("secondaryColor"),
            background=prop("secondaryButton")["colorStatic"]
        )

        combobox = ttk.Combobox(
            gui.window,
            values=game_names,
            width=20,
            state=combobox_state
        )

        def on_game_selection_change(event):
            AppState.set_game(event.widget.get())
            gui.trigger_event(EVENT_GAME_SELECTION_CHANGED)

        # Select first option in dropdown.
        combobox.set(selected_game)
        combobox.pack()

        combobox.place(relx=.9, rely=.05, anchor=tk.N)
        combobox.bind("<<ComboboxSelected>>", on_game_selection_change)
