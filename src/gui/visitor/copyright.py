import tkinter as tk
from datetime import date

from src.core.holders import prop
from src.core.text_resource import tr
from src.gui import GUI, logger
from src.gui.visitor import Visitor


class CopyrightVisitor(Visitor):
    """
    Used to build copyright label.
    Always enabled.
    """

    def __init__(self):
        self.__copyright = None

    def visit(self, gui: GUI):
        self.__add_copyright(gui)

    def refresh(self, gui: GUI):
        period = "2023" if date.today().year == 2023 else f"2023-{date.today().year}"
        copyright_label = tr("window_Copyright", prop("version"), period)

        self.__copyright.configure(text=copyright_label)
        logger.debug("Copyright was reloaded. (%s)", copyright_label)

    def is_enabled(self):
        return True

    def __add_copyright(self, gui: GUI):
        """
        Used to render copyright label.
        """

        self.__copyright = tk.Label(gui.window())
        self.__copyright.place(relx=.5, rely=.9, anchor=tk.N)
