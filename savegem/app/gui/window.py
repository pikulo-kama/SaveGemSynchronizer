from typing import Optional

from PyQt6.QtCore import QMutex, pyqtSignal
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout

from constants import Resource
from savegem.app.gui.style import create_dynamic_resources, load_stylesheet
from savegem.app.gui.widget.manager import WidgetManager
from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.core.context import app
from savegem.common.core.holders import prop
from savegem.common.core.text_resource import tr
from savegem.common.util.file import resolve_resource
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
_gui = None


def gui():
    """
    Used to get instance of GUI.
    """
    global _gui

    if _gui is None:
        _gui = GUI()

    return _gui


class GUI(QMainWindow):
    """
    Main class to operate with application window.
    """

    # Allows to lock/unlock UI.
    # Used to avoid race conditions
    # when UI is being updated from
    # several threads simultaneously.
    mutex = QMutex()

    before_destroy = pyqtSignal()
    after_init = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__application: Optional[QApplication] = None
        self.__manager = WidgetManager(self)

        self.__root = QWidget()
        self.setCentralWidget(self.__root)
        self.__root.setObjectName("root")
        self.__root_layout = QHBoxLayout(self.__root)
        self.__root_layout.setContentsMargins(0, 0, 0, 0)

        self.__is_ui_blocked = False

        self.__center_window()
        self.setWindowTitle(tr("window_Title", prop("name")))
        self.setWindowIcon(QIcon(resolve_resource(Resource.ApplicationIco)))

    @property
    def root(self):
        """
        Central window widget.
        """
        return self.__root

    @property
    def application(self):
        return self.__application

    @application.setter
    def application(self, application: QApplication):
        self.__application = application

    def reload_styles(self):
        """
        Used to reload application styles.
        This includes recalculation of QSS as well
        as recreation of dynamic resources.
        """

        create_dynamic_resources()
        self.application.setStyleSheet(load_stylesheet())

    def build(self):
        """
        Used to build GUI.
        Will use defined builders to build all elements.
        """

        _logger.info("Building UI.")

        self.reload_styles()
        self.__manager.remove_widgets(lambda _: True)
        self.__manager.build()
        self.is_blocked = False

        self.after_init.emit()  # noqa

        _logger.info("Application loop has been started.")
        self.show()

    def refresh(self, event: str = UIRefreshEvent.All):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI.")
        self.__manager.refresh(event)

        self.setWindowTitle(tr("window_Title", prop("name")))

    @property
    def is_blocked(self):
        """
        Used to check if UI is currently blocked to any interactions.
        """
        return self.__is_ui_blocked

    @is_blocked.setter
    def is_blocked(self, is_blocked: bool):
        """
        Used to block/unblock UI.
        """

        self.__is_ui_blocked = is_blocked

        if is_blocked:
            self.__manager.disable()
        else:
            self.__manager.enable()

    def closeEvent(self, event: QCloseEvent):
        """
        Used to call before application window
        destroyed.
        """

        app().state.width = self.width()
        app().state.height = self.height()

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        x = int((screen_width - app().state.width) / 2)
        y = int((screen_height - app().state.height) / 2)

        self.setMinimumSize(prop("minWindowWidth"), prop("minWindowHeight"))
        self.resize(app().state.width, app().state.height)
        self.move(x, y)
