from savegem.app.data import holder
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.dialog import QCustomDialog
from savegem.app.gui.controller.dialog import DialogController
from savegem.app.gui.constants import UISection


class ConfirmationDialogController(DialogController):
    """
    Used to control confirmation dialog.
    Will bind configured callback to confirm button
    and will bind dialog closing to cancel button.
    """

    def setup(self, dialog: QCustomDialog):

        def on_confirm():
            confirm_callback = holder().get("confirmationCallback")

            dialog.hide()
            self.manager.gui.is_blocked = False
            confirm_callback()

        def on_cancel():
            dialog.hide()
            self.manager.gui.is_blocked = False

        confirm_button: QCustomPushButton = self.manager.get_widget(UISection.ConfirmationSection, "confirm_button")
        cancel_button: QCustomPushButton = self.manager.get_widget(UISection.ConfirmationSection, "cancel_button")

        self.manager.gui.is_blocked = True

        confirm_button.enable()
        cancel_button.enable()

        confirm_button.clicked.connect(on_confirm)
        cancel_button.clicked.connect(on_cancel)

        super().setup(dialog)
