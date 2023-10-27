import os.path
import tkinter as tk

from constants import WINDOW_TITLE, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, COPYRIGHT_LABEL, APPLICATION_ICO, \
    PROJECT_ROOT, BTN_PROPERTY_LIST, APPLICATION_VERSION


class GUI:

    def __init__(self):
        self.__window = tk.Tk()
        self.__buttons = list()

        self.__window.title(WINDOW_TITLE)
        self.__window.iconbitmap(os.path.join(PROJECT_ROOT, APPLICATION_ICO))
        self.__window.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.__window.resizable(False, False)

    def build(self):
        self.__add_buttons_internal(self.__window)
        self.__add_copyright_and_version(self.__window)

        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()

    def on_close(self, callback):
        self.__window.protocol('WM_DELETE_WINDOW', callback)

    def add_button(self, name, callback, color):
        self.__buttons.append({
            "name": name,
            "callback": callback,
            "properties": color
        })

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
                fg='#009688',
                bg=button["properties"]["colorStatic"],
                borderwidth=0,
                relief=tk.SOLID,
                pady=15,
                padx=15,
                font=40
            )

            tk_button.bind('<Enter>', on_button_enter)
            tk_button.bind('<Leave>', on_button_leave)

        button_frame.place(relx=.5, rely=.5, anchor=tk.CENTER)

    def __add_copyright_and_version(self, frame):

        horizontal_frame = tk.Frame(frame, pady=-4)

        version_label = tk.Label(horizontal_frame, text=f"v{APPLICATION_VERSION}")
        version_label.grid(row=0, column=0, padx=5)

        copyright_label = tk.Label(horizontal_frame, text=COPYRIGHT_LABEL)
        copyright_label.grid(row=0, column=1)

        horizontal_frame.place(relx=.5, rely=.9, anchor=tk.N)
