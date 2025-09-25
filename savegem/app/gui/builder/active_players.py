from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from savegem.app.gui.constants import UIRefreshEvent, QAttr
from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.window import _GUI
from savegem.app.gui.builder import UIBuilder
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class ActivePlayersBuilder(UIBuilder):
    """
    Used to display section with users
    that currently playing selected game.
    """

    def __init__(self):
        super().__init__(
            UIRefreshEvent.ActivityLogUpdate,
            UIRefreshEvent.GameSelectionChange,
            UIRefreshEvent.LanguageChange
        )

        self.__status_label: QLabel
        self.__active_players_label: QLabel

    def build(self, gui: _GUI):
        self.__add_section(gui)

    def refresh(self, gui: _GUI):
        players_label = tr("label_Offline")
        players_online = len(app.activity.players) > 0
        is_disabled = "true"

        if players_online:
            players_label = app.activity.players.pop(0)
            remaining_players = len(app.activity.players)
            is_disabled = "false"

            if remaining_players > 0:
                players_label += f" +{remaining_players}"

        self.__status_label.setProperty(QAttr.Disabled, is_disabled)
        self.__active_players_label.setProperty(QAttr.Disabled, is_disabled)

        self.__status_label.style().polish(self.__status_label)
        self.__active_players_label.style().polish(self.__active_players_label)

        self.__active_players_label.setText(players_label)

        _logger.debug("Active users section was reloaded. (%s)", players_label)

    def __add_section(self, gui: _GUI):
        """
        Used to render active users section
        containing users that are playing selected
        game at the moment.
        """

        frame = QWidget(gui.top)

        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        self.__status_label = QLabel()
        self.__active_players_label = QLabel()

        self.__status_label.setObjectName("activePlayersBadge")
        self.__active_players_label.setObjectName("activePlayersLabel")

        frame_layout.addStretch(1)
        frame_layout.addWidget(self.__status_label)
        frame_layout.addSpacing(5)
        frame_layout.addWidget(self.__active_players_label)
        frame_layout.addStretch(1)

        gui.top.layout().addWidget(frame, alignment=Qt.AlignmentFlag.AlignTop)
        gui.top.layout().setContentsMargins(0, 20, 0, 0)
