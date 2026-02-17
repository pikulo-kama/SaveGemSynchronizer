from typing import Any, Final

from kui.component.widget import KamaWidget
from kui.core.controller import TemplateWidgetController, TemplateWidgetContext
from kui.core.metadata import ControllerArgs
from kutil.logger import get_logger

from savegem.common.core.context import context

_logger = get_logger(__name__)


class PlayersController(TemplateWidgetController):
    """
    Used to manager player list.
    """

    PlayerActive: Final = "active"

    def retrieve_data(self, args: ControllerArgs) -> list[Any]:
        active_players = context().activity.players
        game_players = context().games.current.players
        players = []

        _logger.debug("Building game player list.")
        _logger.debug("allPlayers=%s", active_players)
        _logger.debug("activePlayers=%s", active_players)

        for player in context().users:
            if len(game_players) > 0 and player.email not in game_players:
                _logger.debug("Player %s doesn't have access to game %s", player.name, context().games.current.name)
                continue

            players.append(player)

        # Sort by name but make sure to show players that are online first.
        players = sorted(players, key=lambda u: (u not in active_players, u.name))
        _logger.debug("gamePlayers=%s", players)

        return players

    def resolve(self, widget_context: TemplateWidgetContext, value: str, *args, **kw):
        if value == "name":
            return widget_context.element.short_name

        elif value == "photo":
            return widget_context.element.photo

        return None

    @classmethod
    def handle__playerCard(cls, player_card: KamaWidget, widget_context: TemplateWidgetContext):  # noqa
        """
        Used to apply style property to players that are currently in-game.
        """

        if widget_context.element in context().activity.players:
            player_card.add_class(cls.PlayerActive)
