from PyQt6.QtCore import QMutex, pyqtSignal
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout

from constants import Resource
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

        self.__main_grid = QGridLayout(self.__root)
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

        self.__main_grid.addWidget(self.top_left, 0, 0)
        self.__main_grid.addWidget(self.top, 0, 1)
        self.__main_grid.addWidget(self.top_right, 0, 2)
        self.__main_grid.addWidget(self.left, 1, 0)
        self.__main_grid.addWidget(self.right, 1, 2)
        self.__main_grid.addWidget(self.bottom_left, 2, 0)
        self.__main_grid.addWidget(self.bottom, 2, 1)
        self.__main_grid.addWidget(self.bottom_right, 2, 2)

        self.__main_grid.setRowStretch(0, 3)
        self.__main_grid.setRowStretch(1, 5)
        self.__main_grid.setRowStretch(2, 1)

        self.__main_grid.setColumnStretch(0, 5)
        self.__main_grid.setColumnStretch(1, 2)
        self.__main_grid.setColumnStretch(2, 5)

        # Center could be quite large that's why it's not part
        # of the main grid.
        center_width = int(self.width() * 0.7)
        center_height = int(self.height() * 0.7)
        x = int((self.width() - center_width) / 2)
        y = int((self.height() - center_height) / 2)

        self.center.setParent(self)
        self.center.setGeometry(x, y, center_width, center_height)
        self.center.raise_()

        self.top_left.setMinimumSize(1, 1)
        self.left.setMinimumSize(1, 1)
        self.bottom_left.setMinimumSize(1, 1)

        self.top_right.setMinimumSize(1, 1)
        self.right.setMinimumSize(1, 1)
        self.bottom_right.setMinimumSize(1, 1)

        for builder_obj in self.__builders:
            builder_obj.build(self)

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
                builder_obj.refresh(self)

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
                builder_obj.disable(self)
            else:
                builder_obj.enable(self)

    def closeEvent(self, event: QCloseEvent):
        """
        Used to destroy application window.
        """

        self.before_destroy.emit()  # noqa
        _logger.info("Application shut down.")

    def __center_window(self):
        """
        Used to center application window.
        Will ensure that each time app opened it's in the center of screen.
        """

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()

        width = prop("windowWidth")
        height = prop("windowHeight")

        alt_width = screen_width - prop("horizontalMargin")
        alt_height = screen_height - prop("verticalMargin")

        width = min(width, alt_width)
        height = min(height, alt_height)

        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)

        self.setFixedSize(width, height)
        self.move(x, y)
