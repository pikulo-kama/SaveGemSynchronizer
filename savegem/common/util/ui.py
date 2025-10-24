from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


def get_color_mode():
    """
    Used to get current color mode.
    """

    mode = "light"
    application = QApplication.instance()

    if application is None:
        return mode

    color_scheme = application.styleHints().colorScheme()  # noqa

    if color_scheme == Qt.ColorScheme.Dark:
        mode = "dark"

    return mode
