import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.style import init_styles
from src.util.file import resolve_resource
from src.util.logger import get_logger

logger = get_logger(__name__)


class GUI:
    """
    Main class to operate with application window.
    """

    _instance = None

    def __init__(self):
        # Just to shup up IDE..
        self.visitors = list()
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

        self.window = tk.Tk()
        self.body_frame = tk.Frame(self.window)
        self.metadata_function = None
        self.visitors = list()

        self.buttons = list()
        self.tk_buttons = list()

        self.save_status = None
        self.last_save_info = None
        self.copyright_label = None
        self.language_button = None

        self.__center_window()

        self.window.title(tr("window_Title"))
        self.window.iconbitmap(resolve_resource("application.ico"))
        self.window.geometry(f"{prop("windowWidth")}x{prop("windowHeight")}")
        self.window.resizable(False, False)

        init_styles()

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

    def register_visitors(self, visitors):
        """
        Used to register visitors.
        """

        for visitor in visitors:

            visitor_name = type(visitor).__name__

            if not visitor.is_enabled():
                logger.warn("Skipping disabled visitor '%s'.", visitor_name)
                continue

            self.visitors.append(visitor)
            logger.info("Registered visitor '%s'", visitor_name)

    def build(self):
        """
        Used to build GUI.
        Will use defined visitors to build all elements.
        """

        logger.info("Building UI.")

        for visitor in self.visitors:
            visitor.visit(self)

        self.body_frame.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.refresh()

        logger.info("Application loop has been started.")
        self.window.mainloop()

    def refresh(self):
        """
        Used to refresh dynamic UI elements.
        """

        logger.info("Refreshing UI.")
        self.window.title(tr("window_Title"))

        for visitor in self.visitors:
            visitor.refresh(self)

    def destroy(self):
        """
        Used to destroy application window.
        """
        self.window.destroy()

    def on_close(self, callback):
        """
        Allows to configure additional callback function that would
        be invoked when window is being destroyed.
        """
        self.window.protocol("WM_DELETE_WINDOW", callback)

    def add_button(self, name, callback, color):
        """
        Used to add main application button.
        """
        self.buttons.append({
            "nameTextResource": name,
            "callback": callback,
            "properties": color
        })

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
