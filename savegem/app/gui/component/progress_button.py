from PyQt6.QtWidgets import QProgressBar

from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.constants import QAttr, QBool


class QProgressPushButton(QCustomPushButton):
    """
    Custom button component.
    Combines both QPushButton and QProgressBar

    When button progress is more than 0 button
    will transform into progress bar.
    """

    __IN_PROGRESS_ATTR = "in-progress"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.__progress_bar = QProgressBar(self)
        self.__progress_bar.setTextVisible(False)
        self.__progress_bar.setValue(0)

    def set_progress(self, progress):
        """
        Used to set progress value of
        progress bar.
        """

        self.__progress_bar.setValue(progress)
        in_progress = progress > 0

        if in_progress:
            self.setText("")

        self.__progress_bar.setTextVisible(in_progress is True)
        self.setProperty(self.__IN_PROGRESS_ATTR, QBool(in_progress))
        self.setEnabled(in_progress is False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update the progress bar's geometry to match the button's size
        self.__progress_bar.setGeometry(0, 0, self.width(), self.height())

    def setProperty(self, name, value):
        super().setProperty(name, value)

        # If kind is being set for
        # button then also update kind
        # of progress bar.
        if name == QAttr.Kind:
            self.__progress_bar.setProperty(QAttr.Kind, f"{self.__class__.__name__}-{value}")
