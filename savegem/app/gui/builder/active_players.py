import tkinter as tk
from tkinter import font

from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.core import app
from savegem.common.core.holders import prop
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

        self.__frame = None
        self.__status_label = None
        self.__active_players_label = None

    def build(self, gui: _GUI):
        self.__add_section(gui)

    def refresh(self, gui: _GUI):

        status_color = "secondaryColor"
        active_players_color = "secondaryColor"
        players_label = tr("label_Offline")

        if len(app.activity.players) > 0:

            status_color = "accentColor"
            active_players_color = "primaryColor"
            players_label = app.activity.players.pop(0)
            remaining_players = len(app.activity.players)

            if remaining_players > 0:
                players_label += f" +{remaining_players}"

        self.__status_label.configure(
            foreground=prop(status_color)
        )

        self.__active_players_label.configure(
            foreground=prop(active_players_color),
            text=players_label
        )

        _logger.debug("Active users section was reloaded. (%s)", players_label)

    def enable(self, gui: "_GUI"):
        pass

    def disable(self, gui: "_GUI"):
        pass

    def __add_section(self, gui: _GUI):
        """
        Used to render active users section.
        """

        self.__frame = tk.Frame(gui.top)

        self.__status_label = tk.Label(
            self.__frame,
            text="⚫",
            font=("Segoe UI Semibold", 10)
        )

        self.__active_players_label = tk.Label(
            self.__frame,
            foreground=prop("primaryColor"),
            font=("Helvetica", 12, font.BOLD)
        )

        self.__status_label.pack(side=tk.LEFT)
        self.__active_players_label.pack(side=tk.LEFT)

        self.__frame.pack(anchor=tk.N, pady=(20, 0))
