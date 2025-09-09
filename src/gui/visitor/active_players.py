import tkinter as tk
from tkinter import font

from src.core import app
from src.core.holders import prop
from src.core.text_resource import tr
from src.gui import _GUI
from src.gui.visitor import Visitor
from src.service.player import PlayerService
from src.util.logger import get_logger

_logger = get_logger(__name__)


class ActivePlayersVisitor(Visitor):
    """
    Used to display section with users
    that currently playing selected game.
    """

    def __init__(self):
        self.__frame = None
        self.__description_label = None
        self.__active_players_label = None

    def visit(self, gui: _GUI):
        self.__add_section(gui)

    def refresh(self, gui: _GUI):
        active_players = PlayerService.get_active_players(app.state.game_name)

        if app.user.name in active_players:
            active_players.remove(app.user.name)

        description_label = ""
        players_label = ""
        border_thickness = 0

        if len(active_players) > 0:
            description_label = tr("label_ActiveUsers")
            border_thickness = 2

            players_label = active_players.pop(0)
            remaining_players = len(active_players)

            if remaining_players > 0:
                players_label += f" +{remaining_players}"

        self.__frame.configure(highlightthickness=border_thickness)
        self.__description_label.configure(text=description_label)
        self.__active_players_label.configure(text=players_label)

        _logger.debug("Active users section was reloaded. (%s%s)", description_label, players_label)

    def disable(self, gui: "_GUI"):
        pass

    def __add_section(self, gui: _GUI):
        """
        Used to render active users section.
        """

        self.__frame = tk.Frame(
            gui.top,
            highlightbackground=prop("secondaryColor"),
            bd=0
        )

        self.__description_label = tk.Label(
            self.__frame,
            fg=prop("primaryColor"),
            font=("Segoe UI Semibold", 10),
            padx=5,
            pady=5
        )
        self.__active_players_label = tk.Label(
            self.__frame,
            fg=prop("primaryColor"),
            font=("Helvetica", 12, font.BOLD),
            padx=5,
            pady=5
        )

        self.__description_label.pack(side=tk.LEFT)
        self.__active_players_label.pack(side=tk.LEFT)

        self.__frame.pack(anchor=tk.N, pady=(20, 0))
