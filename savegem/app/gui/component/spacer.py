from PyQt6.QtWidgets import QWidget, QSizePolicy

from savegem.app.gui.component import CustomComponentMixin


class QSpacer(CustomComponentMixin, QWidget):
    """
    A lightweight spacer component designed to push other widgets aside by
    occupying available layout space.

    This component utilizes an expanding size policy to ensure it consumes
    the maximum possible area within a layout, effectively acting as
    flexible spring or filler.
    """

    def __init__(self):
        """
        Initializes the spacer and configures its size policy to expand
        horizontally while remaining preferred vertically.
        """

        QWidget.__init__(self)
        CustomComponentMixin.__init__(self)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
