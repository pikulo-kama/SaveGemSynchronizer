from kui.component.button import KamaPushButton
from kui.component.dialog import KamaDialog
from kui.core.app import KamaApplication

from savegem.controller.dialog import DialogController
from savegem.constants import UISection


class ConfirmationDialogController(DialogController):
    """
    Used to control confirmation dialog.
    Will bind configured callback to confirm button
    and will bind dialog closing to cancel button.
    """

    def setup(self, dialog: KamaDialog):

        application = KamaApplication()

        def on_confirm():
            confirm_callback = application.data.get("confirmationCallback")

            dialog.hide()
            application.window.is_blocked = False
            confirm_callback()

        def on_cancel():
            dialog.hide()
            application.window.is_blocked = False

        confirm_button: KamaPushButton = self.manager.get_widget(UISection.ConfirmationSection, "confirm_button")
        cancel_button: KamaPushButton = self.manager.get_widget(UISection.ConfirmationSection, "cancel_button")

        application.window.is_blocked = True

        confirm_button.enable()
        cancel_button.enable()

        confirm_button.clicked.connect(on_confirm)
        cancel_button.clicked.connect(on_cancel)

        super().setup(dialog)
