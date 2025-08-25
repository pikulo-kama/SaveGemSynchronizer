import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.util.file import resolve_resource
from src.util.logger import get_logger

logger = get_logger(__name__)


def add_button_hover_effect(button):

    color_mapping = {
        **{btn["colorHover"]: btn["colorStatic"] for btn in [prop("primaryButton"), prop("secondaryButton")]},
        **{btn["colorStatic"]: btn["colorHover"] for btn in [prop("primaryButton"), prop("secondaryButton")]}
    }

    logger.debug("Button hover color mapping - %s", color_mapping)

    def on_button_leave(event):
        event.widget['bg'] = color_mapping[event.widget['bg']]

    def on_button_enter(event):
        event.widget['bg'] = color_mapping[event.widget['bg']]

    button.bind('<Enter>', on_button_enter)
    button.bind('<Leave>', on_button_leave)



class GUI:

    _instance = None

    def __init__(self):
        # Just to shup up IDE..
        self.visitors = list()
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):

        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.__init()

        return cls._instance

    def __init(self):
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

    def register_visitors(self, visitors):

        for visitor in visitors:

            visitor_name = type(visitor).__name__

            if not visitor.is_enabled():
                logger.warn("Skipping disabled visitor '%s'.", visitor_name)
                continue

            self.visitors.append(visitor)
            logger.info("Registered visitor '%s'", visitor_name)

    def build(self):
        logger.info("Building UI.")

        for visitor in self.visitors:
            visitor.visit(self)

        self.body_frame.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.refresh()

        logger.info("Application loop has been started.")
        self.window.mainloop()

    def refresh(self):
        logger.info("Refreshing UI.")
        self.window.title(tr("window_Title"))

        for visitor in self.visitors:
            visitor.refresh(self)

    def destroy(self):
        self.window.destroy()

    def on_close(self, callback):
        self.window.protocol('WM_DELETE_WINDOW', callback)

    def add_button(self, name, callback, color):
        self.buttons.append({
            "nameTextResource": name,
            "callback": callback,
            "properties": color
        })

    def __center_window(self):

        width = prop("windowWidth")
        height = prop("windowHeight")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
