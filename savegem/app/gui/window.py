from typing import Optional

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout

from constants import Resource
from savegem.app.data import holder
from savegem.app.gui.style import create_dynamic_resources, load_stylesheet
from savegem.app.gui.widget.manager import WidgetManager
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.widget.metadata import UISection
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

    before_destroy = pyqtSignal()
    after_init = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__application: Optional[QApplication] = None
        self.__settings = QSettings(prop("author"), prop("name"))
        self.__manager = WidgetManager(self)

        self.__root = QWidget()
        self.setCentralWidget(self.__root)
        self.__root.setObjectName("root")
        self.__root_layout = QHBoxLayout(self.__root)
        self.__root_layout.setContentsMargins(0, 0, 0, 0)

        self.__is_ui_blocked = False
        self.__is_wait_screen = False
        self.__is_initialized = False

        self.__center_window()
        self.setWindowIcon(QIcon(resolve_resource(Resource.ApplicationIco)))

    @property
    def root(self):
        """
        Central window widget.
        """
        return self.__root

    @property
    def application(self):
        """
        QT Application instance.
        """
        return self.__application

    @application.setter
    def application(self, application: QApplication):
        """
        Used to attach QT Application instance
        to the window instance.
        """
        self.__application = application

    def reload_styles(self):
        """
        Used to reload application styles.
        This includes recalculation of QSS as well
        as recreation of dynamic resources.
        """

        create_dynamic_resources()
        self.application.setStyleSheet(load_stylesheet())

    def show(self):

        if not self.__is_initialized:
            self.after_init.emit()  # noqa
            self.__is_initialized = True

        super().show()
        _logger.info("Application loop has been started.")

    def build(self, section: str = UISection.RootSection):
        """
        Used to build window and all of its components.
        """

        self.setWindowTitle(tr("window_Title", prop("name")))
        _logger.info("Building UI using section '%s'.", section)

        self.reload_styles()
        self.__manager.remove_widgets(lambda _: True)
        self.__manager.build(section)
        self.is_blocked = False

        self.show()

    def refresh(self, event: str = UIRefreshEvent.All):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI with event '%s'.", event)
        self.__manager.refresh(event)

        self.setWindowTitle(tr("window_Title", prop("name")))

    def notification(self, message: str):
        """
        Used to present notification dialog
        using provided message.
        """

        holder().add("dialogMessage", message)
        self.__manager.build("notification")

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

        self.__settings.setValue("windowWidth", self.width())
        self.__settings.setValue("windowHeight", self.height())

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        user_screen_width = self.__settings.value("windowWidth", prop("windowWidth"))
        user_screen_height = self.__settings.value("windowHeight", prop("windowHeight"))

        x = int((screen_width - user_screen_width) / 2)
        y = int((screen_height - user_screen_height) / 2)

        self.setMinimumSize(prop("minWindowWidth"), prop("minWindowHeight"))
        self.resize(user_screen_width, user_screen_height)
        self.move(x, y)
