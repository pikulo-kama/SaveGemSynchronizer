import tkinter as tk
from tkinter import font

from src.core.holders import prop
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor


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

        refresh_button = tk.Button(
            gui.window,
            text="⟳",
            command=gui.refresh,
            font=("Small Fonts", 18, font.BOLD),
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            bg=prop("primaryButton")["colorStatic"],
            fg=prop("primaryColor")
        )

        refresh_button.pack()
        refresh_button.place(relx=.05, rely=.05, anchor=tk.N)
