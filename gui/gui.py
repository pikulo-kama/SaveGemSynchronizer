import os.path
import tkinter as tk
from datetime import datetime, timedelta

from babel.dates import format_datetime

from constants import WINDOW_TITLE, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, COPYRIGHT_LABEL, APPLICATION_ICO, \
    PROJECT_ROOT, BTN_PROPERTY_LIST, APPLICATION_VERSION, SAVE_VERSION_FILE_NAME, SAVE_UP_TO_DATE_LABEL, \
    SAVE_OUTDATED_LABEL, LAST_SAVE_INFO_LABEL, APPLICATION_PRIMARY_TEXT_COLOR, APPLICATION_SECONDARY_TEXT_COLOR, \
    APPLICATION_LOCALE, TZ_PLUS_HOURS
from gui.gui_event_listener import GuiEventListener
from service.user_service import UserService




class GUI:

    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):

        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            cls._instance.__init()

        return cls._instance

    def __init(self):
        self.window = tk.Tk()
        self.__buttons = list()
        self.__last_save_func = None

        self.__center_window()

        self.window.title(WINDOW_TITLE)
        self.window.iconbitmap(os.path.join(PROJECT_ROOT, APPLICATION_ICO))
        self.window.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.window.resizable(False, False)

    def build(self):

        body_frame = tk.Frame(self.window)

        self.__add_last_save_info(body_frame)
        self.__add_buttons_internal(body_frame)
        self.__add_active_users_section(self.window)
        self.__add_copyright_and_version(self.window)

        body_frame.place(relx=.5, rely=.3, anchor=tk.CENTER)

        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    def on_close(self, callback):
        self.window.protocol('WM_DELETE_WINDOW', callback)

    def add_button(self, name, callback, color):
        self.__buttons.append({
            "name": name,
            "callback": callback,
            "properties": color
        })

    def trigger_event(self, event, context=None):
        GuiEventListener().handle_event(event, self, context)

    def set_last_save_func(self, func):
        self.__last_save_func = func

    def __add_last_save_info(self, frame):
        info_frame = tk.Frame(frame)
        latest_save = self.__last_save_func()

        print(latest_save['createdTime'])
        date_info = self.extract_date(latest_save["createdTime"])

        self.save_status = tk.Label(
            info_frame,
            text=self.get_last_download_version_text(latest_save),
            fg=APPLICATION_PRIMARY_TEXT_COLOR,
            font=("Helvetica", 25)
        )
        self.last_save_info = tk.Label(
            info_frame,
            text=str(LAST_SAVE_INFO_LABEL.format(date_info["date"], date_info["time"], latest_save["owner"])),
            fg=APPLICATION_SECONDARY_TEXT_COLOR,
            font=("Helvetica", 11, 'bold')
        )

        self.save_status.grid(row=0, column=0, pady=5)
        self.last_save_info.grid(row=1, column=0, pady=5)

        info_frame.grid(row=0, column=0, pady=150)

    def __add_buttons_internal(self, frame):

        def on_button_leave(e):
            color_mapping = {btn["colorHover"]: btn["colorStatic"] for btn in BTN_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        def on_button_enter(e):
            color_mapping = {btn["colorStatic"]: btn["colorHover"] for btn in BTN_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        button_frame = tk.Frame(frame)

        for idx, button in enumerate(self.__buttons):
            tk_button = tk.Button(
                button_frame,
                width=button["properties"]["width"],
                text=button["name"],
                command=button["callback"]
            )

            tk_button.grid(row=0, column=idx, padx=5)
            tk_button.config(
                fg=APPLICATION_PRIMARY_TEXT_COLOR,
                bg=button["properties"]["colorStatic"],
                borderwidth=0,
                relief=tk.SOLID,
                pady=15,
                padx=15,
                font=40
            )

            tk_button.bind('<Enter>', on_button_enter)
            tk_button.bind('<Leave>', on_button_leave)

        button_frame.grid(row=1, column=0)

    def __add_active_users_section(self, frame):

        user_data = UserService().get_user_data()

        vertical_frame = tk.Frame(frame, pady=5)

        for idx, user in enumerate(user_data):

            user_frame = tk.Frame(vertical_frame)

            user_label = tk.Label(
                user_frame,
                fg=APPLICATION_SECONDARY_TEXT_COLOR,
                text=user["name"],
                justify="left",
                anchor="w"
            )
            user_state_label = tk.Label(
                user_frame,
                text="⚫",
                fg="#32CD32" if user["isPlaying"] else "#DC143C",
                justify="left",
                anchor="w"
            )

            user_state_label.grid(row=0, column=0)
            user_label.grid(row=0, column=1)

            user_frame.grid(row=idx, column=0, sticky=tk.W)

        vertical_frame.place(rely=.865, relx=.95, anchor=tk.NE)

    def __create_state_canvas(self, frame, is_playing):

        canvas = tk.Canvas(frame)
        canvas.create_oval(10, 10, 10, 10, fill="#32CD32" if is_playing else "#DC143C")

        return canvas

    def __add_copyright_and_version(self, frame):

        horizontal_frame = tk.Frame(frame, pady=-4)

        version_label = tk.Label(horizontal_frame, text=f"v{APPLICATION_VERSION}")
        version_label.grid(row=0, column=0, padx=5)

        copyright_label = tk.Label(horizontal_frame, text=COPYRIGHT_LABEL)
        copyright_label.grid(row=0, column=1)

        horizontal_frame.place(relx=.5, rely=.9, anchor=tk.N)

    def get_last_download_version_text(self, latest_save):
        save_version_file_name = os.path.join(PROJECT_ROOT, SAVE_VERSION_FILE_NAME)
        last_downloaded_version = None

        if os.path.isfile(save_version_file_name):
            with open(save_version_file_name, 'r') as save_version_file:
                last_downloaded_version = save_version_file.read()

        if last_downloaded_version is None:
            save_status_message = ""

        elif last_downloaded_version == latest_save["name"]:
            save_status_message = SAVE_UP_TO_DATE_LABEL

        else:
            save_status_message = SAVE_OUTDATED_LABEL

        return save_status_message

    def extract_date(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        date += timedelta(hours=TZ_PLUS_HOURS)

        return {
            "date": format_datetime(date, "d MMMM", locale=APPLICATION_LOCALE),
            "time": date.strftime("%H:%M")
        }

    def __center_window(self):

        width = WINDOW_DEFAULT_WIDTH
        height = WINDOW_DEFAULT_HEIGHT

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) / 2
        y = (screen_height - height) / 2

        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
