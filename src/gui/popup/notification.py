import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui import GUI
from src.util.file import resolve_resource


def notification(message: str):
    Notification().show_notification(message)


class Notification:

    def __init__(self):
        self.__window = tk.Tk()
        self.__center_window(GUI.instance())

    def show_notification(self, message):

        def on_button_leave(event):
            event.widget['bg'] = prop("primaryButton")['colorStatic']

        def on_button_enter(event):
            event.widget['bg'] = prop("primaryButton")['colorHover']

        self.__window.geometry(f"{prop("popupWidth")}x{prop("popupHeight")}")
        self.__window.title(tr("popup_NotificationTitle"))
        self.__window.iconbitmap(resolve_resource("notification.ico"))
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window)

        message_label = tk.Label(
            container,
            text=message,
            fg=prop("secondaryColor"),
            font=('Helvetica', 10, 'bold')
        )

        close_btn = tk.Button(
            container,
            text=tr("popup_NotificationButtonClose"),
            width=20,
            command=lambda: self.__window.destroy()
        )

        close_btn.config(
            fg=prop("secondaryColor"),
            bg=prop("primaryButton")["colorStatic"],
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

    def __center_window(self, gui):
        popup_width = prop("popupWidth")
        popup_height = prop("popupHeight")

        self.__window.geometry('%dx%d+%d+%d' % (
            popup_width,
            popup_height,
            gui.window.winfo_rootx() + ((prop("windowWidth") - popup_width) / 2),
            gui.window.winfo_rooty())
        )
