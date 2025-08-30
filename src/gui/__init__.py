import tkinter as tk

from src.core.text_resource import tr
from src.core.holders import prop
from src.gui.visitor import load_visitors, Visitor
from src.util.file import resolve_resource
from src.util.logger import get_logger

_logger = get_logger(__name__)


class _GUI:
    """
    Main class to operate with application window.
    """

    def __init__(self):
        """
        Used to initialize GUI.
        """

        self.__window = tk.Tk()
        self.__body = tk.Frame(self.window)

        from src.gui.style import init_gui_styles
        init_gui_styles()

        self.__visitors: list[Visitor] = list()
        self.__before_destroy_callback = None
        self.__is_ui_blocked = False

        self.__center_window()
        self.window.title(tr("window_Title"))
        self.window.iconbitmap(resolve_resource("application.ico"))
        self.window.geometry(f"{prop("windowWidth")}x{prop("windowHeight")}")
        self.window.resizable(False, False)

        self.window.protocol("WM_DELETE_WINDOW", self.destroy)

    def initialize(self):
        """
        Used to post initialize necessary resources for GUI.
        """
        self.__visitors = load_visitors()

    @property
    def is_blocked(self):
        """
        Used to check if UI is currently blocked to any interactions.
        """
        return self.__is_ui_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked: bool):
        """
        Used to block/unblock UI.
        """
        self.__is_ui_blocked = is_blocked

        if is_blocked:
            for visitor_obj in self.__visitors:
                visitor_obj.disable(self)

        else:
            self.refresh()

    @property
    def window(self):
        """
        Used to get root widget.
        """
        return self.__window

    @property
    def body(self):
        """
        Used to get main widget which is direct child of root.
        Works with more central area of the window (compared to root)
        """
        return self.__body

    def set_cursor(self, cursor=""):
        """
        Used to change main window cursor.
        """
        self.window.config(cursor=cursor)

    def schedule_operation(self, callback):
        """
        Used by processes executed on separate thread to execute some work back on main thread.
        This is needed since Tkinter doesn't work well with multithreading.
        """
        self.window.after(0, callback)

    def build(self):
        """
        Used to build GUI.
        Will use defined visitors to build all elements.
        """

        _logger.info("Building UI.")

        for visitor_obj in self.__visitors:
            visitor_obj.visit(self)

        self.body.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.refresh()

        _logger.info("Application loop has been started.")
        self.window.mainloop()

    def refresh(self):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI.")
        for visitor_obj in self.__visitors:
            visitor_obj.refresh(self)

        self.window.title(tr("window_Title"))

    def destroy(self):
        """
        Used to destroy application window.
        """

        if self.__before_destroy_callback is not None:
            self.__before_destroy_callback()

        self.window.destroy()

    def before_destroy(self, callback):
        """
        Allows to configure additional callback function that would
        be invoked when window is being destroyed.
        """
        self.__before_destroy_callback = callback

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        width = prop("windowWidth")
        height = prop("windowHeight")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.window.geometry("%dx%d+%d+%d" % (width, height, x, y))


gui = _GUI()
