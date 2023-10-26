import os.path
import tkinter as tk
from tkinter import ttk

from constants import WINDOW_TITLE, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT, COPYRIGHT_LABEL, APPLICATION_ICO, \
    PROJECT_ROOT


class GUI:

    def __init__(self):
        self.__window = tk.Tk()
        self.__buttons = list()

        self.__window.title(WINDOW_TITLE)
        self.__window.iconbitmap(os.path.join(PROJECT_ROOT, APPLICATION_ICO))
        self.__window.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.__window.resizable(False, False)

        ttk.Style().configure("TButton", padding=40, font=30)

    def build(self):
        self.__add_buttons_internal()
        copyright_label = tk.Label(self.__window, text=COPYRIGHT_LABEL, pady=-4)
        copyright_label.place(relx=.5, rely=.9, anchor=tk.N)
        self.__window.mainloop()

    def destroy(self):
        self.__window.destroy()

    def on_close(self, callback):
        self.__window.protocol('WM_DELETE_WINDOW', callback)

    def add_button(self, name, callback):
        self.__buttons.append({
            "name": name,
            "callback": callback
        })

    def __add_buttons_internal(self):
        button_frame = tk.Frame(self.__window)

        for idx, button in enumerate(self.__buttons):
            tk_button = ttk.Button(
                button_frame,
                width=int(40),
                text=button["name"],
                command=button["callback"]
            )
            tk_button.grid(row=idx, column=0, pady=5)

        button_frame.place(relx=.5, rely=.5, anchor=tk.CENTER)
