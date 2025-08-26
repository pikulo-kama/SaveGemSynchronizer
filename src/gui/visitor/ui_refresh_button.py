import tkinter as tk
from tkinter import ttk

from src.gui import GUI
from src.gui.style import add_button_movement_effect
from src.gui.visitor import Visitor


class UIRefreshButtonVisitor(Visitor):
    """
    Used to render UI refresh button.
    Always enabled.
    """

    def visit(self, gui: GUI):
        self.__add_refresh_button(gui)

    def refresh(self, gui: GUI):
        pass

    def is_enabled(self):
        return True

    @staticmethod
    def __add_refresh_button(gui):
        """
        Used to render UI refresh button.
        """

        refresh_button = ttk.Button(
            gui.window(),
            text="⟳",
            command=gui.refresh,
            cursor="hand2",
            padding=(4, 7),
            style="SquarePrimary.18.TButton",
            takefocus=False
        )

        add_button_movement_effect(refresh_button)
        refresh_button.pack()
        refresh_button.place(relx=.05, rely=.05, anchor=tk.N)
