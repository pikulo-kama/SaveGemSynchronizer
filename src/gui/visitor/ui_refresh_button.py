import tkinter as tk

from src.gui import GUI
from src.gui.component.wait_button import WaitButton
from src.gui.style import add_button_movement_effect
from src.gui.visitor import Visitor
from src.util.thread import execute_in_thread


class UIRefreshButtonVisitor(Visitor):
    """
    Used to render UI refresh button.
    Always enabled.
    """

    def __init__(self):
        self.__refresh_button = None

    def visit(self, gui: GUI):
        self.__add_refresh_button(gui)

    def refresh(self, gui: GUI):
        self.__refresh_button.configure(text="⟳")

    def is_enabled(self):
        return True

    def __add_refresh_button(self, gui):
        """
        Used to render UI refresh button.
        """

        self.__refresh_button = WaitButton(
            gui.window(),
            command=lambda: execute_in_thread(gui.refresh),
            cursor="hand2",
            padding=(4, 7),
            style="SquarePrimary.18.TButton",
            takefocus=False
        )

        add_button_movement_effect(self.__refresh_button)
        self.__refresh_button.pack()
        self.__refresh_button.place(relx=.05, rely=.05, anchor=tk.N)
