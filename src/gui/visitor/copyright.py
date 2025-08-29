import tkinter as tk
from datetime import date

from src.core.holders import prop
from src.core.text_resource import tr
from src.gui import _GUI
from src.gui.visitor import Visitor
from src.util.logger import get_logger

_logger = get_logger(__name__)


class CopyrightVisitor(Visitor):
    """
    Used to build copyright label.
    Always enabled.
    """

    def __init__(self):
        self.__copyright = None

    def visit(self, gui: _GUI):
        self.__add_copyright(gui)

    def refresh(self, gui: _GUI):
        period = "2023" if date.today().year == 2023 else f"2023-{date.today().year}"
        copyright_label = tr("window_Copyright", prop("version"), period)

        self.__copyright.configure(text=copyright_label)
        _logger.debug("Copyright was reloaded. (%s)", copyright_label)

    def is_enabled(self):
        return True

    def __add_copyright(self, gui: _GUI):
        """
        Used to render copyright label.
        """

        self.__copyright = tk.Label(gui.window)
        self.__copyright.place(relx=.5, rely=.9, anchor=tk.N)
