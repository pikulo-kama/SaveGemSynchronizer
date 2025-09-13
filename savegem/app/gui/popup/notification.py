from savegem.common.core.text_resource import tr
from savegem.app.gui import gui, TkCursor
from savegem.app.gui.component.button import Button
from savegem.app.gui.popup import Popup


def notification(message: str):
    """
    Used to display notification message.
    """
    gui.schedule_operation(lambda: Notification().show(message))


class Notification(Popup):
    """
    Popup used to display notification messages.
    """

    def __init__(self):
        super().__init__("popup_NotificationTitle", "notification.ico")

    def _show_internal(self):
        close_btn = Button(
            self._container,
            text=tr("popup_NotificationButtonClose"),
            cursor=TkCursor.Hand,
            width=20,
            command=self.destroy,
            style="SmallPrimary.TButton"
        )

        close_btn.grid(row=1, column=0)
