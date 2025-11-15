from PyQt6.QtWidgets import QProgressBar

from savegem.app.gui.component import CustomComponentMixin


class QWaitBar(QProgressBar, CustomComponentMixin):
    """
    Progress bar used to represent that some action is running.
    Doesn't show actual progress.
    """

    def __init__(self):
        QProgressBar.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setRange(0, 0)
