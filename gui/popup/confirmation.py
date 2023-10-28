import os
import tkinter as tk

from constants import CONFIRMATION_WINDOW_CONFIRM_BTN, CONFIRMATION_WINDOW_CLOSE_BTN, CONFIRMATION_WINDOW_WIDTH, \
    CONFIRMATION_WINDOW_HEIGHT, CONFIRMATION_WINDOW_TITLE, CONFIRMATION_ICO, PROJECT_ROOT, NOTIFICATION_TEXT_COLOR, \
    CONFIRMATION_TEXT_COLOR, CONFIRMATION_CONFIRM_BTN_PROPERTIES, CONFIRMATION_CANCEL_BTN_PROPERTIES, \
    CONFIRMATION_POPUP_PROPERTY_LIST


class Confirmation:

    def __init__(self):
        self.__window = tk.Tk()

    def show_notification(self, message, callback):

        def on_button_leave(e):
            color_mapping = {btn["colorHover"]: btn["colorStatic"] for btn in CONFIRMATION_POPUP_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        def on_button_enter(e):
            color_mapping = {btn["colorStatic"]: btn["colorHover"] for btn in CONFIRMATION_POPUP_PROPERTY_LIST}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        self.__window.geometry(f"{CONFIRMATION_WINDOW_WIDTH}x{CONFIRMATION_WINDOW_HEIGHT}")
        self.__window.title(CONFIRMATION_WINDOW_TITLE)
        self.__window.iconbitmap(os.path.join(PROJECT_ROOT, CONFIRMATION_ICO))
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window)
        container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        message_label = tk.Label(
            container,
            text=message,
            fg=CONFIRMATION_TEXT_COLOR,
            font=('Helvetica', 10, 'bold')
        )

        button_frame = tk.Frame(container)

        confirm_btn = tk.Button(
            button_frame,
            text=CONFIRMATION_WINDOW_CONFIRM_BTN,
            width=10,
            command=callback
        )

        close_btn = tk.Button(
            button_frame,
            text=CONFIRMATION_WINDOW_CLOSE_BTN,
            width=10,
            command=lambda: self.__window.destroy()
        )

        confirm_btn.config(
            fg=CONFIRMATION_TEXT_COLOR,
            bg=CONFIRMATION_CONFIRM_BTN_PROPERTIES["colorStatic"],
            borderwidth=0,
            relief=tk.SOLID,
            pady=5,
            padx=5,
            font=4
        )

        close_btn.config(
            fg=CONFIRMATION_TEXT_COLOR,
            bg=CONFIRMATION_CANCEL_BTN_PROPERTIES["colorStatic"],
            borderwidth=0,
            relief=tk.SOLID,
            pady=5,
            padx=5,
            font=4
        )

        confirm_btn.bind('<Enter>', on_button_enter)
        confirm_btn.bind('<Leave>', on_button_leave)

        close_btn.bind('<Enter>', on_button_enter)
        close_btn.bind('<Leave>', on_button_leave)

        confirm_btn.grid(row=0, column=0, padx=20)
        close_btn.grid(row=0, column=1)

        message_label.grid(row=0, column=0, pady=20)
        button_frame.grid(row=1, column=0)

        container.place(relx=.5, rely=.5)

        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()
