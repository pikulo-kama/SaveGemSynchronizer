from typing import Any, Final

from kui.component.button import KamaPushButton
from kui.core.constants import QBool
from kui.core.controller import TemplateWidgetController
from kutil.logger import get_logger

from savegem.constants import UIRefreshEvent
from savegem.app.worker.game_change_worker import GameChangeWorker
from savegem.common.core.context import context
from savegem.common.core.game_config import Game
from savegem.common.core.save_meta import SyncStatus


_logger = get_logger(__name__)


class GameListController(TemplateWidgetController):
    """
    Used to manage game list widget.
    """

    GameOptionSelected: Final = "selected"
    GameOptionWarning: Final = "warning"

    def _get_data(self) -> list[Any]:
        return context().games

    def handle__game_option(self, game_button: KamaPushButton, game: Game):
        """
        Used to link callback to game option and apply
        style properties to it.
        """

        def change_name(game_name: str):
            return lambda: self.__change_game(game_name)

        game_button.clicked.connect(change_name(game.name))  # noqa

        if game == context().games.current:
            game_button.setProperty(self.GameOptionSelected, QBool(True))

        if game.meta.sync_status != SyncStatus.UpToDate:
            game_button.setProperty(self.GameOptionWarning, QBool(True))

    def resolve(self, game: Game, value: str, *args, **kw):
        if value == "name":
            return game.name

        return None

    def __change_game(self, new_game):
        """
        Used to change currently selected game.
        """

        if new_game == context().state.game_name:
            return

        _logger.info("Game selection changed.")
        _logger.info("Old = %s, New = %s", context().state.game_name, new_game)

        worker = GameChangeWorker(new_game)
        worker.finished.connect(lambda: self.manager.event_refresh(UIRefreshEvent.GameSelectionChange))

        self._do_work(worker)
