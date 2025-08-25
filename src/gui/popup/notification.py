import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.popup.popup import Popup, add_button_hover_effect


def notification(message: str):
    Notification().show(message)


class Notification(Popup):

    def __init__(self):
        super().__init__("popup_NotificationTitle", "notification.ico")

    def _show_internal(self):

        close_btn = tk.Button(
            self._container,
            text=tr("popup_NotificationButtonClose"),
            width=20,
            command=self.destroy
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

        add_button_hover_effect(close_btn)
        close_btn.grid(row=1, column=0)
