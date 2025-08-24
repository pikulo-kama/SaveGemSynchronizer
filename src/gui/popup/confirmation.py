import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui import GUI
from src.util.file import resolve_resource


class Confirmation:

    def __init__(self):
        self.__window = tk.Tk()
        self.__center_window(GUI.instance())

    def show_confirmation(self, message, callback):

        confirmation_popup_property_list = [prop("primaryButton"), prop("secondaryButton")]

        def on_button_leave(e):
            color_mapping = {btn["colorHover"]: btn["colorStatic"] for btn in confirmation_popup_property_list}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        def on_button_enter(e):
            color_mapping = {btn["colorStatic"]: btn["colorHover"] for btn in confirmation_popup_property_list}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        self.__window.geometry(f"{prop("popupWidth")}x{prop("popupHeight")}")
        self.__window.title(tr("popup_ConfirmationTitle"))
        self.__window.iconbitmap(resolve_resource("confirmation.ico"))
        self.__window.resizable(False, False)

        container = tk.Frame(self.__window)
        container.place(relx=.5, rely=.5, anchor=tk.CENTER)

        message_label = tk.Label(
            container,
            text=message,
            fg=prop("secondaryColor"),
            font=('Helvetica', 10, 'bold')
        )

        button_frame = tk.Frame(container)

        confirm_btn = tk.Button(
            button_frame,
            text=tr("popup_ConfirmationButtonConfirm"),
            width=10,
            command=callback
        )

        close_btn = tk.Button(
            button_frame,
            text=tr("popup_ConfirmationButtonClose"),
            width=10,
            command=lambda: self.__window.destroy()
        )

        confirm_btn.config(
            fg=prop("secondaryColor"),
            bg=prop("primaryButton")["colorStatic"],
            borderwidth=0,
            relief=tk.SOLID,
            pady=5,
            padx=5,
            font=4
        )

        close_btn.config(
            fg=prop("secondaryColor"),
            bg=prop("secondaryButton")["colorStatic"],
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

    def __center_window(self, gui):

        popup_width = prop("popupWidth")
        popup_height = prop("popupHeight")

        self.__window.geometry('%dx%d+%d+%d' % (
            popup_width,
            popup_height,
            gui.window.winfo_rootx() + ((prop("windowWidth") - popup_width) / 2),
            gui.window.winfo_rooty())
        )
