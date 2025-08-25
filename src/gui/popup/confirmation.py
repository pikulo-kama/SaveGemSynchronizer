import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.popup.popup import Popup, add_button_hover_effect


class Confirmation(Popup):

    def __init__(self):
        super().__init__("popup_ConfirmationTitle", "confirmation.ico")
        self.__confirm_callback = None

    def set_confirm_callback(self, callback):
        self.__confirm_callback = callback

    def _show_internal(self):
        button_frame = tk.Frame(self._container)

        confirm_btn = tk.Button(
            button_frame,
            text=tr("popup_ConfirmationButtonConfirm"),
            width=10,
            command=self.__confirm_callback
        )
        close_btn = tk.Button(
            button_frame,
            text=tr("popup_ConfirmationButtonClose"),
            width=10,
            command=self.destroy
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

        add_button_hover_effect(confirm_btn)
        add_button_hover_effect(close_btn)

        confirm_btn.grid(row=0, column=0, padx=20)
        close_btn.grid(row=0, column=1)

        button_frame.grid(row=1, column=0)
