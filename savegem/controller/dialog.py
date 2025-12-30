from kui.component.dialog import KamaDialog
from kui.core.app import KamaApplication
from kui.core.controller import WidgetController


class DialogController(WidgetController):
    """
    Used to control dialog components.
    Will update parent by linking dialog
    directly to the main window instance.

    Will display dialog so it will appear
    on top of other components.
    """

    def setup(self, dialog: KamaDialog):
        application = KamaApplication()

        dialog.setParent(application.window)
        dialog.adjustSize()
        dialog.exec()
