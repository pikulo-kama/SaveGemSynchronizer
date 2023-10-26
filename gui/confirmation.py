import tkinter as tk

from constants import CONFIRMATION_WINDOW_CONFIRM_BTN, CONFIRMATION_WINDOW_CLOSE_BTN, CONFIRMATION_WINDOW_WIDTH, \
    CONFIRMATION_WINDOW_HEIGHT, CONFIRMATION_WINDOW_TITLE


class Confirmation:

    def __init__(self):
        self.__window = tk.Tk()

    def show_notification(self, message, callback):

        self.__window.geometry(f"{CONFIRMATION_WINDOW_WIDTH}x{CONFIRMATION_WINDOW_HEIGHT}")
        self.__window.title(CONFIRMATION_WINDOW_TITLE)
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window, pady=40)
        container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        message_label = tk.Label(container, text=message)
        message_label.grid(row=0, column=0)

        button_frame = tk.Frame(self.__window)

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

        button_frame.place(relx=.5, rely=.7, anchor=tk.N)
        confirm_btn.grid(row=0, column=0, padx=20)
        close_btn.grid(row=0, column=1)

        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()
