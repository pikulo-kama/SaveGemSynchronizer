import tkinter as tk
from src.core import app
from src.gui import _GUI
from src.gui.constants import TkState, TkCursor, TkEvent
from src.gui.visitor import Visitor
from tkinter import ttk, font

from src.util.logger import get_logger
from src.util.thread import execute_in_thread

_logger = get_logger(__name__)


class GameDropdownVisitor(Visitor):
    """
    Used to build game selection dropdown.
    Always enabled. If there are no games configured app will crash.
    """

    def __init__(self):
        self.__combobox = None

    @property
    def order(self) -> int:
        # Needs to be initialized first.
        return 0

    def visit(self, gui: _GUI):
        self.__add_game_selection_dropdown(gui)

    def refresh(self, gui: _GUI):

        app.games.download()

        if app.games.empty:
            _logger.error("There are no games configured. Can't proceed.")
            raise RuntimeError("There are no games configured. Can't proceed.")

        game_names = app.games.names

        combobox_state = TkState.Readonly
        combobox_cursor = TkCursor.Hand

        if len(game_names) == 1:
            combobox_state = TkState.Disabled
            combobox_cursor = TkCursor.Forbidden

        self.__combobox.configure(
            values=game_names,
            state=combobox_state,
            cursor=combobox_cursor
        )

        self.__combobox.set(app.state.game_name)

    def disable(self, gui: "_GUI"):
        self.__combobox.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_game_selection_dropdown(self, gui: _GUI):
        """
        Used to render game selection dropdown.
        """

        def on_game_selection_change(event):
            _logger.info("Game selection changed.")
            _logger.info("Selected game - %s", event.widget.get())

            app.state.game_name = event.widget.get()
            gui.refresh()

        self.__combobox = ttk.Combobox(
            gui.top_right,
            width=20,
            font=("Helvetica", 10, font.BOLD),
            style="Secondary.TCombobox"
        )

        self.__combobox.bind(TkEvent.ComboboxSelected, lambda e: execute_in_thread(lambda: on_game_selection_change(e)))
        self.__combobox.place(relx=1, rely=.2, x=-20, y=20, anchor=tk.NE)
