import tkinter as tk
from savegem.common.core import app
from savegem.app.gui import _GUI
from savegem.app.gui.component.dropdown import Dropdown
from savegem.app.gui.constants import TkState, TkCursor
from savegem.app.gui.visitor import Visitor

from savegem.common.util.logger import get_logger
from savegem.common.util.thread import execute_in_thread

_logger = get_logger(__name__)


class GameDropdownVisitor(Visitor):
    """
    Used to build game selection dropdown.
    Always enabled. If there are no games configured app will crash.
    """

    def __init__(self):
        self.__dropdown = None

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

        self.__dropdown.configure(
            values=game_names,
            state=combobox_state,
            cursor=combobox_cursor
        )

        self.__dropdown.set(app.state.game_name)

    def disable(self, gui: "_GUI"):
        self.__dropdown.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_game_selection_dropdown(self, gui: _GUI):
        """
        Used to render game selection dropdown.
        """

        def on_game_selection_change(value):
            def callback():
                _logger.info("Game selection changed.")
                _logger.info("Selected game - %s", value)

                app.state.game_name = value
                gui.refresh()

            return execute_in_thread(callback)

        self.__dropdown = Dropdown(
            gui.top_right,
            width=25,
            height=1.5,
            prefix="🎮 ",
            command=on_game_selection_change,
            margin=(10, 0),
            style="Secondary.TDropdown"
        )

        self.__dropdown.grid(row=1, column=0, sticky=tk.E, padx=(0, 20), pady=(10, 0))
