import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.style import init_gui_styles
from src.util.file import resolve_resource
from src.util.logger import get_logger

logger = get_logger(__name__)


class GUI:
    """
    Main class to operate with application window.
    """

    _instance = None

    def __init__(self):
        # Just to shut up Pylint...
        self.__visitors = list()
        self.__destroy_callback = None
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        """
        Used to get GUI instance.
        """

        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.__init()

        return cls._instance

    def __init(self):
        """
        Used to initialize GUI.
        """

        self.__visitors = list()
        self.__destroy_callback = None

        self.__window = tk.Tk()
        self.__body = tk.Frame(self.__window)

        self.__center_window()
        self.__window.title(tr("window_Title"))
        self.__window.iconbitmap(resolve_resource("application.ico"))
        self.__window.geometry(f"{prop("windowWidth")}x{prop("windowHeight")}")
        self.__window.resizable(False, False)

        self.__window.protocol("WM_DELETE_WINDOW", self.destroy)
        init_gui_styles()

    def window(self):
        """
        Used to get root widget.
        """
        return self.__window

    def body(self):
        """
        Used to get main widget which is direct child of body.
        Affects more center area of the window (compared to root)
        """
        return self.__body

    def set_cursor(self, cursor=""):
        """
        Used to change main window cursor.
        """
        self.__window.config(cursor=cursor)

    def schedule_operation(self, callback):
        """
        Used by processes executed on separate thread to execute some work back on main thread.
        This is needed since Tkinter doesn't work well with multithreading.
        """
        self.__window.after(0, callback)

    def register_visitors(self, visitors):
        """
        Used to register visitors.
        """

        for visitor in visitors:
            visitor_name = type(visitor).__name__

            if not visitor.is_enabled():
                logger.warn("Skipping disabled visitor '%s'.", visitor_name)
                continue

            self.__visitors.append(visitor)
            logger.info("Registered visitor '%s'", visitor_name)

    def build(self):
        """
        Used to build GUI.
        Will use defined visitors to build all elements.
        """

        logger.info("Building UI.")

        for visitor in self.__visitors:
            visitor.visit(self)

        self.__body.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.refresh()

        logger.info("Application loop has been started.")
        self.__window.mainloop()

    def refresh(self):
        """
        Used to refresh dynamic UI elements.
        """

        logger.info("Refreshing UI.")
        for visitor in self.__visitors:
            visitor.refresh(self)

        self.__window.title(tr("window_Title"))

    def destroy(self):
        """
        Used to destroy application window.
        """

        if self.__destroy_callback is not None:
            self.__destroy_callback()

        self.__window.destroy()

    def before_destroy(self, callback):
        """
        Allows to configure additional callback function that would
        be invoked when window is being destroyed.
        """
        self.__destroy_callback = callback

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        width = prop("windowWidth")
        height = prop("windowHeight")

        screen_width = self.__window.winfo_screenwidth()
        screen_height = self.__window.winfo_screenheight()

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.__window.geometry("%dx%d+%d+%d" % (width, height, x, y))
