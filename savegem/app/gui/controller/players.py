from typing import Any, Final

from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import QAttr
from savegem.app.gui.controller import TemplateWidgetController
from savegem.common.core.context import app
from savegem.common.core.user import User
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class PlayersController(TemplateWidgetController):
    """
    Used to manager player list.
    """

    PlayerActive: Final = "active"

    def _get_data(self) -> list[Any]:
        active_players = app().activity.players
        game_players = app().games.current.players
        players = []

        _logger.debug("Building game player list.")
        _logger.debug("allPlayers=%s", active_players)
        _logger.debug("activePlayers=%s", active_players)

        for player in app().users:
            if len(game_players) > 0 and player.email not in game_players:
                _logger.debug("Player %s doesn't have access to game %s", player.name, app().games.current.name)
                continue

            players.append(player)

        # Sort by name but make sure to show players that are online first.
        players = sorted(players, key=lambda u: (u not in active_players, u.name))
        _logger.debug("gamePlayers=%s", players)

        return players

    def resolve(self, player: User, value: str, *args, **kw):
        if value == "name":
            return player.short_name

        elif value == "photo":
            return player.photo

        return None

    @classmethod
    def handle__player_card(cls, player_card: QCustomWidget, player: User):
        """
        Used to apply style property to players that are currently in-game.
        """

        if player in app().activity.players:
            player_card.setProperty(QAttr.Id, cls.PlayerActive)
