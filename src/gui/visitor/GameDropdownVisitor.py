from src.core.AppState import AppState
from src.core.holders import games
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from tkinter import ttk, font
import tkinter as tk

from src.util.logger import get_logger

logger = get_logger(__name__)


class GameDropdownVisitor(Visitor):
    """
    Used to build game selection dropdown.
    Always enabled. If there are no games configured app will crash.
    """

    def visit(self, gui: GUI):
        self.__add_game_selection_dropdown(gui)

    def is_enabled(self):
        # Visitor should be enabled always even if there is one game, so it would still be obvious what game
        # is selected.
        if len(games()) == 0:
            logger.error("There are no games configured in config/games.json. Can't proceed.")
            raise RuntimeError("There are no games configured in config/games.json. Can't proceed.")

        return True

    def refresh(self, gui: GUI):
        pass

    @staticmethod
    def __add_game_selection_dropdown(gui: GUI):
        """
        Used to render game selection dropdown.
        """

        game_names = [game["name"] for game in games()]
        selected_game = AppState.get_game(game_names[0])

        combobox_state = "readonly"
        combobox_cursor = "hand2"

        if len(game_names) == 1:
            combobox_state = "disabled"
            combobox_cursor = "no"

        combobox = ttk.Combobox(
            gui.window,
            values=game_names,
            cursor=combobox_cursor,
            font=("Helvetica", 10, font.BOLD),
            width=20,
            state=combobox_state,
            style="Secondary.TCombobox"
        )

        def on_game_selection_change(event):
            logger.info("Game selection changed.")
            logger.info("Selected game - %s", event.widget.get())

            AppState.set_game(event.widget.get())
            gui.refresh()

        # Select first option in dropdown.
        combobox.set(selected_game)
        combobox.pack()

        combobox.place(relx=.9, rely=.05, width=150, height=30, anchor=tk.N)
        combobox.bind("<<ComboboxSelected>>", on_game_selection_change)
