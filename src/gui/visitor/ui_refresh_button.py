import tkinter as tk

from src.gui import _GUI
from src.gui.component.wait_button import WaitButton
from src.gui.visitor import Visitor
from src.util.thread import execute_in_thread


class UIRefreshButtonVisitor(Visitor):
    """
    Used to render UI refresh button.
    Always enabled.
    """

    def __init__(self):
        self.__refresh_button = None

    def visit(self, gui: _GUI):
        self.__add_refresh_button(gui)

    def refresh(self, gui: _GUI):
        self.__refresh_button.configure(text="⟳", state="", cursor="hand2")

    def disable(self, gui: "_GUI"):
        self.__refresh_button.configure(state="disabled", cursor="wait")

    def is_enabled(self):
        return True

    def __add_refresh_button(self, gui):
        """
        Used to render UI refresh button.
        """

        self.__refresh_button = WaitButton(
            gui.window,
            # This is funny part... Since execute_in_thread already refresh UI
            # there is no need to pass gui.refresh here since it will result in
            # UI refreshing twice.
            command=lambda: execute_in_thread(lambda: None),
            padding=(4, 7),
            style="SquarePrimary.18.TButton",
            takefocus=False
        )

        self.__refresh_button.pack()
        self.__refresh_button.place(relx=.05, rely=.05, anchor=tk.N)
