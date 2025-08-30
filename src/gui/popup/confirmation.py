import tkinter as tk

from src.core.text_resource import tr
from src.gui import TkCursor
from src.gui.component.button import Button
from src.gui.popup import Popup


def confirmation(message: str, callback):
    """
    Present popup used to display confirmation messages.
    """
    popup = Confirmation()
    popup.set_confirm_callback(callback)
    popup.show(message)


class Confirmation(Popup):
    """
    Popup used to display confirmation messages.
    """

    def __init__(self):
        super().__init__("popup_ConfirmationTitle", "confirmation.ico")
        self.__confirm_callback = None

    def set_confirm_callback(self, callback):
        """
        Used to set callback that would be executed
        when Confirm button is bein clicked.
        """

        self.__confirm_callback = callback

    def _show_internal(self):
        button_frame = tk.Frame(self._container)

        def confirm_callback():
            if self.__confirm_callback is not None:
                self.__confirm_callback()

            self.destroy()

        confirm_btn = Button(
            button_frame,
            text=tr("popup_ConfirmationButtonConfirm"),
            cursor=TkCursor.Hand,
            width=12,
            command=confirm_callback,
            style="SmallPrimary.TButton"
        )

        close_btn = Button(
            button_frame,
            text=tr("popup_ConfirmationButtonClose"),
            cursor=TkCursor.Hand,
            width=10,
            command=self.destroy,
            style="SmallSecondary.TButton"
        )

        confirm_btn.grid(row=0, column=0, padx=(10, 10))
        close_btn.grid(row=0, column=1)

        button_frame.grid(row=1, column=0)
