import tkinter as tk

from savegem.app.gui.ipc_socket import ui_socket
from savegem.common.core import app
from savegem.app.gui.window import _GUI
from savegem.app.gui.component.dropdown import Dropdown
from savegem.app.gui.constants import TkState, TkCursor, UIRefreshEvent
from savegem.app.gui.visitor import Visitor
from savegem.common.core.ipc_socket import IPCCommand

from savegem.common.util.logger import get_logger
from savegem.common.util.thread import execute_in_blocking_thread

_logger = get_logger(__name__)


class GameDropdownVisitor(Visitor):
    """
    Used to build game selection dropdown.
    Always enabled. If there are no games configured app will crash.
    """

    def __init__(self):
        super().__init__(
            UIRefreshEvent.GameConfigChange,
            UIRefreshEvent.GameSelectionChange
        )
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

        self.__dropdown.configure(values=app.games.names)
        self.__dropdown.set(app.games.current.name)

        self.enable(gui)

    def enable(self, gui: "_GUI"):
        state = TkState.Readonly
        cursor = TkCursor.Hand

        if len(app.games.names) == 1:
            state = TkState.Disabled
            cursor = TkCursor.Forbidden

        self.__dropdown.configure(state=state, cursor=cursor)

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
                ui_socket.notify_children(IPCCommand.StateChanged)
                gui.refresh(UIRefreshEvent.GameSelectionChange)

            return execute_in_blocking_thread(callback)

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
