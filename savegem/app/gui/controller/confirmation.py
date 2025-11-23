from savegem.app.data import holder
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.dialog import QCustomDialog
from savegem.app.gui.controller.dialog import DialogController
from savegem.app.gui.widget.metadata import UISection


class ConfirmationDialogController(DialogController):

    def setup(self, dialog: QCustomDialog):

        def on_confirm():
            confirm_callback = holder().get("confirmationCallback")

            dialog.hide()
            confirm_callback()

        confirm_button: QCustomPushButton = self.manager.get_widget(UISection.ConfirmSection, "confirm_button")
        cancel_button: QCustomPushButton = self.manager.get_widget(UISection.ConfirmSection, "cancel_button")

        confirm_button.enable()
        cancel_button.enable()

        confirm_button.clicked.connect(on_confirm)
        cancel_button.clicked.connect(lambda: dialog.hide())

        super().setup(dialog)
