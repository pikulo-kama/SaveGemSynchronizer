from src.core.AppState import AppState
from src.core.GameConfig import GameConfig
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

    def __init__(self):
        self.__combobox = None

    def visit(self, gui: GUI):
        self.__add_game_selection_dropdown(gui)

    def is_enabled(self):
        return True

    def refresh(self, gui: GUI):

        GameConfig.download()

        if len(GameConfig.games()) == 0:
            logger.error("There are no games configured. Can't proceed.")
            raise RuntimeError("There are no games configured. Can't proceed.")

        game_names = GameConfig.game_names()
        default_game = game_names[0]
        selected_game = AppState.get_game(default_game)

        if selected_game not in game_names:
            selected_game = default_game
            AppState.set_game(default_game)

        combobox_state = "readonly"
        combobox_cursor = "hand2"

        if len(game_names) == 1:
            combobox_state = "disabled"
            combobox_cursor = "no"

        self.__combobox.configure(
            values=game_names,
            cursor=combobox_cursor,
            state=combobox_state,
        )

        self.__combobox.set(selected_game)

    def __add_game_selection_dropdown(self, gui: GUI):
        """
        Used to render game selection dropdown.
        """

        def on_game_selection_change(event):
            logger.info("Game selection changed.")
            logger.info("Selected game - %s", event.widget.get())

            AppState.set_game(event.widget.get())
            gui.refresh()

        self.__combobox = ttk.Combobox(
            gui.window(),
            font=("Helvetica", 10, font.BOLD),
            width=20,
            style="Secondary.TCombobox"
        )

        self.__combobox.pack()
        self.__combobox.place(relx=.9, rely=.05, width=150, height=30, anchor=tk.N)
        self.__combobox.bind("<<ComboboxSelected>>", on_game_selection_change)
