import abc
from abc import abstractmethod
import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui import GUI
from src.util.file import resolve_resource
from src.util.logger import get_logger

logger = get_logger(__name__)


class Popup(abc.ABC):
    """
    Tkinter wrapper for popups.
    """

    def __init__(self, title_text_resource, icon):
        gui = GUI.instance()

        self.__popup = tk.Toplevel(gui.window)
        self.__center_window(gui)

        self.__popup.transient(gui.window)
        self.__popup.grab_set()

        self.__title_text_resource = title_text_resource
        self.__icon = icon
        self._container = None

    def show(self, message):
        """
        Used to display popup with provided message.
        """

        logger.info("Initializing popup.")

        logger.debug("popupTitle = %s", self.__title_text_resource)
        logger.debug("popupMessage = %s", message)

        self.__popup.geometry(f"{prop("popupWidth")}x{prop("popupHeight")}")
        self.__popup.title(tr(self.__title_text_resource))
        self.__popup.iconbitmap(resolve_resource(self.__icon))
        self.__popup.resizable(False, False)

        self._container = tk.Frame(self.__popup)

        message_label = tk.Label(
            self._container,
            text=message,
            fg=prop("secondaryColor"),
            font=("Helvetica", 10, "bold")
        )

        self._show_internal()

        message_label.grid(row=0, column=0, pady=20)
        self._container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.__popup.mainloop()

    @abstractmethod
    def _show_internal(self):
        """
        Should be overridden in child classes.
        Should be used to add additional or customize existing
        controls in popup.
        """
        pass

    def destroy(self):
        """
        Used to destroy window context.
        """

        self.__popup.destroy()
        logger.info("Popup has been destroyed.")

    def __center_window(self, gui):
        """
        Used to center popup against main application window.
        """

        popup_width = prop("popupWidth")
        popup_height = prop("popupHeight")
        window_width = prop("windowWidth")

        window_x = gui.window.winfo_rootx()
        offset_x = window_x + ((window_width - popup_width) / 2)
        offset_y = gui.window.winfo_rooty()

        logger.debug("popupXPosition = %d", offset_x)
        logger.debug("popupYPosition = %d", offset_y)

        self.__popup.geometry("%dx%d+%d+%d" % (
            popup_width,
            popup_height,
            offset_x,
            offset_y
        ))
