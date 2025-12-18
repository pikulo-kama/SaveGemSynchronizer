from PyQt6.QtWidgets import QProgressBar

from savegem.app.gui.component import CustomComponentMixin


class QWaitBar(CustomComponentMixin, QProgressBar):
    """
    A specialized progress bar used to indicate that a background process is active.

    Unlike a standard progress bar, this component is intended for indeterminate
    waiting periods where the exact completion percentage is unknown.
    """

    def __init__(self):
        """
        Initializes the wait bar in an indeterminate state by setting the
        range to (0, 0).
        """

        QProgressBar.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setRange(0, 0)
