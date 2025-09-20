import tkinter as tk

from constants import Resource
from savegem.common.core.text_resource import tr
from savegem.common.core.holders import prop
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.builder import load_builders, UIBuilder
from savegem.common.util.file import resolve_resource
from savegem.common.util.logger import get_logger

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

        self.__top_left = tk.Frame(self.window)
        self.__top = tk.Frame(self.window)
        self.__top_right = tk.Frame(self.window)
        self.__left = tk.Frame(self.window)
        self.__center = tk.Frame(self.window)
        self.__right = tk.Frame(self.window)
        self.__bottom_left = tk.Frame(self.window)
        self.__bottom = tk.Frame(self.window)
        self.__bottom_right = tk.Frame(self.window)

        from savegem.app.gui.style import init_gui_styles
        init_gui_styles()

        self.__builders: list[UIBuilder] = list()
        self.__before_destroy_callback = None
        self.__after_init_callback = None
        self.__is_ui_blocked = False

        self.__center_window()
        self.window.title(tr("window_Title", prop("name")))
        self.window.iconbitmap(resolve_resource(Resource.ApplicationIco))
        self.window.resizable(False, False)

        self.window.protocol("WM_DELETE_WINDOW", self.destroy)

    def initialize(self):
        """
        Used to post initialize necessary resources for GUI.
        """
        self.__builders = load_builders()

    @property
    def window(self):
        """
        Used to get root widget.
        """
        return self.__window

    @property
    def top_left(self):
        """
        Used to get top left area of widget.
        """
        return self.__top_left

    @property
    def top(self):
        """
        Used to get top area of widget.
        """
        return self.__top

    @property
    def top_right(self):
        """
        Used to get top right area of widget.
        """
        return self.__top_right

    @property
    def left(self):
        """
        Used to get left area of widget.
        """
        return self.__left

    @property
    def center(self):
        """
        Used to get center area of widget.
        """
        return self.__center

    @property
    def right(self):
        """
        Used to get right area of widget.
        """
        return self.__right

    @property
    def bottom_left(self):
        """
        Used to get bottom left area of widget.
        """
        return self.__bottom_left

    @property
    def bottom(self):
        """
        Used to get bottom area of widget.
        """
        return self.__bottom

    @property
    def bottom_right(self):
        """
        Used to get bottom right area of widget.
        """
        return self.__bottom_right

    def set_cursor(self, cursor):
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
        Will use defined builders to build all elements.
        """

        _logger.info("Building UI.")

        for builder_obj in self.__builders:
            builder_obj.build(self)

        self.window.rowconfigure(0, weight=3)
        self.window.rowconfigure(1, weight=5)
        self.window.rowconfigure(2, weight=1)

        self.window.columnconfigure(0, weight=5, minsize=100)
        self.window.columnconfigure(1, weight=2, minsize=100)
        self.window.columnconfigure(2, weight=5, minsize=100)

        self.top_left.grid(row=0, column=0, sticky=tk.NSEW)
        self.top.grid(row=0, column=1, sticky=tk.NSEW)
        self.top_right.grid(row=0, column=2, sticky=tk.NSEW)
        self.left.grid(row=1, column=0, sticky=tk.NSEW)
        self.right.grid(row=1, column=2, sticky=tk.NSEW)
        self.bottom_left.grid(row=2, column=0, sticky=tk.NSEW)
        self.bottom.grid(row=2, column=1, sticky=tk.NSEW)
        self.bottom_right.grid(row=2, column=2, sticky=tk.NSEW)

        self.top_right.columnconfigure(0, weight=1)

        # Center could be quite large that's why it's not part
        # of the main grid.
        self.center.place(relx=.5, rely=.5, anchor=tk.CENTER)
        self.center.lift()

        self.top_left.grid_propagate(False)
        self.left.grid_propagate(False)
        self.bottom_left.grid_propagate(False)

        self.top_right.grid_propagate(False)
        self.right.grid_propagate(False)
        self.bottom_right.grid_propagate(False)

        self.refresh()
        self.is_blocked = False

        if self.__after_init_callback is not None:
            self.__after_init_callback()

        _logger.info("Application loop has been started.")
        self.window.mainloop()

    def after_init(self, callback):
        """
        Used to define callback that will trigger
        when GUI application is initialized.
        """
        self.__after_init_callback = callback

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

        for builder_obj in self.__builders:

            if is_blocked:
                builder_obj.disable(self)
            else:
                builder_obj.enable(self)

    def refresh(self, *events):
        """
        Used to refresh dynamic UI elements.
        """

        # If no events where provided then attempt
        # to reload all components.
        if len(events) == 0:
            events = [UIRefreshEvent.Always]

        _logger.info("Refreshing UI.")
        for builder_obj in self.__builders:

            if any(event in builder_obj.events for event in events):
                builder_obj.refresh(self)

        self.window.title(tr("window_Title", prop("name")))

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

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        width = prop("windowWidth")
        height = prop("windowHeight")

        alt_width = screen_width - prop("horizontalMargin")
        alt_height = screen_height - prop("verticalMargin")

        width = min(width, alt_width)
        height = min(height, alt_height)

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.window.geometry("%dx%d+%d+%d" % (width, height, x, y))


gui = _GUI()
