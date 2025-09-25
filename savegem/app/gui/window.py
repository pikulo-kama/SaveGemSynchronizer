from PyQt6.QtCore import QMutex, pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QStackedLayout

from constants import Resource
from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.common.core.holders import prop
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.builder import load_builders, UIBuilder
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
        _gui = _GUI()

    return _gui


class _GUI(QMainWindow):
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
        """
        Used to initialize GUI.
        """
        super().__init__()

        self.__root = QWidget()
        self.setCentralWidget(self.__root)
        self.__root_layout = QStackedLayout(self.__root)
        self.__root_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.__grid_widget = QWidget()
        self.__grid_layout = QGridLayout(self.__grid_widget)
        self.__top_left = QWidget()
        self.__top = QWidget()
        self.__top_right = QWidget()
        self.__left = QWidget()
        self.__center = QWidget()
        self.__right = QWidget()
        self.__bottom_left = QWidget()
        self.__bottom = QWidget()
        self.__bottom_right = QWidget()

        self.__builders: list[UIBuilder] = load_builders()
        self.__is_ui_blocked = False

        self.__center_window()
        self.setWindowTitle(tr("window_Title", prop("name")))
        self.setWindowIcon(QIcon(resolve_resource(Resource.ApplicationIco)))

    @property
    def top_left(self):
        """
        Used to get top left area of widget.
        """
        return self.__top_left

    @property
    def top(self):
        """
        Used to get top area of widget.
        """
        return self.__top

    @property
    def top_right(self):
        """
        Used to get top right area of widget.
        """
        return self.__top_right

    @property
    def left(self):
        """
        Used to get left area of widget.
        """
        return self.__left

    @property
    def center(self):
        """
        Used to get center area of widget.
        """
        return self.__center

    @property
    def right(self):
        """
        Used to get right area of widget.
        """
        return self.__right

    @property
    def bottom_left(self):
        """
        Used to get bottom left area of widget.
        """
        return self.__bottom_left

    @property
    def bottom(self):
        """
        Used to get bottom area of widget.
        """
        return self.__bottom

    @property
    def bottom_right(self):
        """
        Used to get bottom right area of widget.
        """
        return self.__bottom_right

    def build(self):
        """
        Used to build GUI.
        Will use defined builders to build all elements.
        """

        _logger.info("Building UI.")

        # Two row grid
        top_left_layout = QGridLayout(self.top_left)
        top_left_layout.setContentsMargins(20, 20, 0, 0)
        top_left_layout.setRowStretch(2, 1)
        top_left_layout.setVerticalSpacing(10)

        self.top.setLayout(QVBoxLayout())

        # Two row grid
        top_right_layout = QGridLayout(self.top_right)
        top_right_layout.setContentsMargins(0, 20, 20, 0)
        top_right_layout.setRowStretch(2, 1)
        top_right_layout.setColumnStretch(0, 1)
        top_right_layout.setVerticalSpacing(10)

        self.center.setLayout(QGridLayout())
        self.bottom.setLayout(QHBoxLayout())

        self.__grid_layout.addWidget(self.top_left, 0, 0)
        self.__grid_layout.addWidget(self.top, 0, 1)
        self.__grid_layout.addWidget(self.top_right, 0, 2)
        self.__grid_layout.addWidget(self.left, 1, 0)
        self.__grid_layout.addWidget(self.right, 1, 2)
        self.__grid_layout.addWidget(self.bottom_left, 2, 0)
        self.__grid_layout.addWidget(self.bottom, 2, 1)
        self.__grid_layout.addWidget(self.bottom_right, 2, 2)

        self.__grid_layout.setRowStretch(0, 3)
        self.__grid_layout.setRowStretch(1, 5)
        self.__grid_layout.setRowStretch(2, 1)

        self.__grid_layout.setColumnStretch(0, 5)
        self.__grid_layout.setColumnStretch(1, 2)
        self.__grid_layout.setColumnStretch(2, 5)

        self.top_left.setMinimumSize(1, 1)
        self.left.setMinimumSize(1, 1)
        self.bottom_left.setMinimumSize(1, 1)

        self.top_right.setMinimumSize(1, 1)
        self.right.setMinimumSize(1, 1)
        self.bottom_right.setMinimumSize(1, 1)

        # Center could be quite large that's why it's not part
        # of the main grid.
        center_wrapper = QWidget()
        center_wrapper_layout = QHBoxLayout(center_wrapper)
        center_wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center_layout = QVBoxLayout(self.center)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center.setMaximumWidth(round(prop("windowWidth") * 0.7))
        self.center.setMinimumHeight(round(prop("windowHeight") * 0.5))

        center_wrapper_layout.addWidget(self.center)
        self.__root_layout.addWidget(self.__grid_widget)
        self.__root_layout.addWidget(center_wrapper)

        for builder_obj in self.__builders:
            builder_obj.link(self)
            builder_obj.build()

        self.refresh()
        self.is_blocked = False

        self.after_init.emit()  # noqa

        _logger.info("Application loop has been started.")
        self.show()

    def refresh(self, event=UIRefreshEvent.All):
        """
        Used to refresh dynamic UI elements.
        """

        _logger.info("Refreshing UI.")
        for builder_obj in self.__builders:

            if event in builder_obj.events:
                builder_obj.refresh()

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

        for builder_obj in self.__builders:

            if is_blocked:
                builder_obj.disable()
            else:
                builder_obj.enable()

    def closeEvent(self, event: QCloseEvent):
        """
        Used to call before application window
        destroyed.
        """

        app.state.width = self.width()
        app.state.height = self.height()

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        x = int((screen_width - app.state.width) / 2)
        y = int((screen_height - app.state.height) / 2)

        self.setMinimumSize(prop("minWindowWidth"), prop("minWindowHeight"))
        self.resize(app.state.width, app.state.height)
        self.move(x, y)
