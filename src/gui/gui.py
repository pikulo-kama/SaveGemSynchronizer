import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.util.file import resolve_resource


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

    def build(self, visitors):

        self.visitors = list(filter(lambda v: v.is_enabled(), visitors))

        for visitor in self.visitors:
            visitor.visit(self)

        self.body_frame.place(relx=.5, rely=.3, anchor=tk.CENTER)

        self.refresh()
        self.window.mainloop()

    def refresh(self):
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
