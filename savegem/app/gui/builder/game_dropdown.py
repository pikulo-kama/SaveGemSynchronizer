from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QComboBox

from savegem.app.gui.component.combobox import QCustomComboBox
from savegem.app.gui.worker.game_change_worker import GameChangeWorker
from savegem.common.core.context import app
from savegem.app.gui.constants import UIRefreshEvent, QObjectName, QAttr, QKind
from savegem.app.gui.builder import UIBuilder

from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class GameDropdownBuilder(UIBuilder):
    """
    Used to build game selection dropdown.
    Always enabled. If there are no games configured app will crash.
    """

    def __init__(self):
        super().__init__(
            UIRefreshEvent.GameConfigChange,
            UIRefreshEvent.GameSelectionChange
        )
        self.__combobox: Optional[QComboBox] = None

    def build(self):
        """
        Used to render game selection dropdown.
        """

        self.__combobox = QCustomComboBox()
        self.__combobox.setObjectName(QObjectName.ComboBox)
        self.__combobox.setProperty(QAttr.Kind, QKind.Secondary)
        self.__combobox.currentTextChanged.connect(self.__change_game)  # noqa

        self._add_interactable(self.__combobox)

        self._gui.top_right.layout().addWidget(self.__combobox, 1, 1)

    def refresh(self):

        if app().games.empty:
            _logger.error("There are no games configured. Can't proceed.")
            raise RuntimeError("There are no games configured. Can't proceed.")

        self.__combobox.blockSignals(True)
        self.__combobox.clear()
        self.__combobox.addItems(app().games.names)
        self.__combobox.view().setCursor(Qt.CursorShape.PointingHandCursor)

        self.__combobox.setCurrentText(app().games.current.name)
        self.__combobox.blockSignals(False)

        self.enable()

    def enable(self):
        enabled = True
        cursor = Qt.CursorShape.PointingHandCursor

        if len(app().games.names) == 1:
            enabled = False
            cursor = Qt.CursorShape.ForbiddenCursor

        self.__combobox.setEnabled(enabled)
        self.__combobox.setCursor(QCursor(cursor))

    def __change_game(self, new_game):
        _logger.info("Game selection changed.")
        _logger.info("Selected game - %s", new_game)

        worker = GameChangeWorker(new_game)
        worker.finished.connect(lambda: self._gui.refresh(UIRefreshEvent.GameSelectionChange))

        self._do_work(worker)
