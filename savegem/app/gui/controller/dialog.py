from savegem.app.gui.component.dialog import QCustomDialog
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.window import gui


class DialogController(WidgetController):
    """
    Used to control dialog components.
    Will update parent by linking dialog
    directly to the main window instance.

    Will display dialog so it will appear
    on top of other components.
    """

    def setup(self, dialog: QCustomDialog):
        dialog.setParent(gui())
        dialog.adjustSize()
        dialog.exec()
