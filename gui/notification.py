import tkinter as tk

from constants import NOTIFICATION_WINDOW_TITLE, NOTIFICATION_WINDOW_WIDTH, NOTIFICATION_WINDOW_HEIGHT, \
    NOTIFICATION_WINDOW_CLOSE_BTN


class Notification:

    def __init__(self):
        self.__window = tk.Tk()

    def show_notification(self, message):
        self.__window.geometry(f"{NOTIFICATION_WINDOW_WIDTH}x{NOTIFICATION_WINDOW_HEIGHT}")
        self.__window.title(NOTIFICATION_WINDOW_TITLE)
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window, pady=40)
        container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        message_label = tk.Label(container, text=message)
        message_label.grid(row=0, column=0)

        close_btn = tk.Button(
            container,
            text=NOTIFICATION_WINDOW_CLOSE_BTN,
            width=40,
            command=lambda: self.__window.destroy()
        )
        close_btn.grid(row=1, column=0)

        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()
