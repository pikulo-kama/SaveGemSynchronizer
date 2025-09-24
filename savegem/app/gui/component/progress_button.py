from PyQt6.QtWidgets import QPushButton, QProgressBar

from savegem.app.gui.constants import QAttr


class QProgressPushButton(QPushButton):
    """
    Custom button component.
    Combines both QPushButton and QProgressBar

    When button progress is more than 0 button
    will transform into progress bar.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.__progres_bar = QProgressBar(self)
        self.__progres_bar.setTextVisible(False)
        self.__progres_bar.setValue(0)

    def set_progress(self, progress):
        """
        Used to set progress value of
        progress bar.
        """

        self.__progres_bar.setValue(progress)

        if progress > 0:
            self.setText("")
            self.__progres_bar.setTextVisible(True)
            self.setEnabled(False)

        else:
            self.__progres_bar.setTextVisible(False)
            self.setEnabled(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update the progress bar's geometry to match the button's size
        self.__progres_bar.setGeometry(0, 0, self.width(), self.height())

    def setProperty(self, name, value):
        super().setProperty(name, value)

        # If kind is being set for
        # button then also update kind
        # of progress bar.
        if name == QAttr.Kind:
            self.__progres_bar.setProperty(QAttr.Kind, f"{self.__class__.__name__}-{value}")
