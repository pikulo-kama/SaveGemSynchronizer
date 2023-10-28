import os
import tkinter as tk

from constants import NOTIFICATION_WINDOW_TITLE, NOTIFICATION_WINDOW_WIDTH, NOTIFICATION_WINDOW_HEIGHT, \
    NOTIFICATION_WINDOW_CLOSE_BTN, PROJECT_ROOT, NOTIFICATION_ICO, NOTIFICATION_TEXT_COLOR, \
    NOTIFICATION_POPUP_PROPERTY_LIST, NOTIFICATION_CLOSE_BTN_PROPERTIES


class Notification:

    def __init__(self):
        self.__window = tk.Tk()

    def show_notification(self, message):

        def on_button_leave(e):
            color_mapping = {btn["colorHover"]: btn["colorStatic"] for btn in NOTIFICATION_POPUP_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        def on_button_enter(e):
            color_mapping = {btn["colorStatic"]: btn["colorHover"] for btn in NOTIFICATION_POPUP_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        self.__window.geometry(f"{NOTIFICATION_WINDOW_WIDTH}x{NOTIFICATION_WINDOW_HEIGHT}")
        self.__window.title(NOTIFICATION_WINDOW_TITLE)
        self.__window.iconbitmap(os.path.join(PROJECT_ROOT, NOTIFICATION_ICO))
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window)

        message_label = tk.Label(
            container,
            text=message,
            fg=NOTIFICATION_TEXT_COLOR,
            font=('Helvetica', 10, 'bold')
        )

        close_btn = tk.Button(
            container,
            text=NOTIFICATION_WINDOW_CLOSE_BTN,
            width=20,
            command=lambda: self.__window.destroy()
        )

        close_btn.config(
            fg=NOTIFICATION_TEXT_COLOR,
            bg=NOTIFICATION_CLOSE_BTN_PROPERTIES["colorStatic"],
            borderwidth=0,
            relief=tk.SOLID,
            pady=5,
            padx=5,
            font=4
        )

        close_btn.bind('<Enter>', on_button_enter)
        close_btn.bind('<Leave>', on_button_leave)

        message_label.grid(row=0, column=0, pady=20)
        close_btn.grid(row=1, column=0)

        container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()
