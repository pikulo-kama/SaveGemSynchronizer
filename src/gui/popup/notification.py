from tkinter import ttk

from src.core.text_resource import tr
from src.gui import GUI
from src.gui.popup import Popup


def notification(message: str):
    """
    Used to display notification message.
    """
    GUI.instance().schedule_operation(lambda: Notification().show(message))


class Notification(Popup):
    """
    Popup used to display notification messages.
    """

    def __init__(self):
        super().__init__("popup_NotificationTitle", "notification.ico")

    def _show_internal(self):

        close_btn = ttk.Button(
            self._container,
            text=tr("popup_NotificationButtonClose"),
            cursor="hand2",
            width=20,
            command=self.destroy,
            style="SmallPrimary.TButton",
            takefocus=False
        )

        close_btn.grid(row=1, column=0)
