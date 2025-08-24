import os.path
import tkinter as tk

from constants import PROJECT_ROOT, SAVE_VERSION_FILE_NAME
from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui_event_listener import GuiEventListener
from src.util.file import resolve_resource


class GUI:

    _instance = None

    def __init__(self):
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

        self.buttons = list()
        self.last_save_func = None

        self.save_status = None
        self.last_save_info = None

        self.__center_window()

        self.window.title(tr("window_Title"))
        self.window.iconbitmap(resolve_resource("valheim_synchronizer.ico"))
        self.window.geometry(f"{prop("windowWidth")}x{prop("windowHeight")}")
        self.window.resizable(False, False)

    def build(self, visitors):

        for visitor in visitors:

            if visitor.is_enabled():
                visitor.visit(self)

        self.body_frame.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    def on_close(self, callback):
        self.window.protocol('WM_DELETE_WINDOW', callback)

    def add_button(self, name, callback, color):
        self.buttons.append({
            "name": name,
            "callback": callback,
            "properties": color
        })

    def trigger_event(self, event, context=None):
        GuiEventListener.handle_event(event, self, context)

    def get_last_download_version_text(self, latest_save):
        save_version_file_name = os.path.join(PROJECT_ROOT, SAVE_VERSION_FILE_NAME)
        last_downloaded_version = None

        if os.path.isfile(save_version_file_name):
            with open(save_version_file_name, 'r') as save_version_file:
                last_downloaded_version = save_version_file.read()

        if last_downloaded_version is None:
            save_status_message = ""

        elif last_downloaded_version == latest_save["name"]:
            save_status_message = tr("info_SaveIsUpToDate")

        else:
            save_status_message = tr("info_SaveNeedsToBeDownloaded")

        return save_status_message

    def __center_window(self):

        width = prop("windowWidth")
        height = prop("windowHeight")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
