from typing import Any, Final

from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.constants import UIRefreshEvent, QBool
from savegem.app.gui.controller import TemplateWidgetController
from savegem.app.worker.game_change_worker import GameChangeWorker
from savegem.common.core.context import app
from savegem.common.core.game_config import Game
from savegem.common.core.save_meta import SyncStatus
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class GameListController(TemplateWidgetController):
    """
    Used to manage game list widget.
    """

    GameOptionSelected: Final = "selected"
    GameOptionWarning: Final = "warning"

    def _get_data(self) -> list[Any]:
        return app().games

    def handle__game_option(self, game_button: QCustomPushButton, game: Game):
        """
        Used to link callback to game option and apply
        style properties to it.
        """

        def change_name(game_name: str):
            return lambda: self.__change_game(game_name)

        game_button.clicked.connect(change_name(game.name))  # noqa

        if game == app().games.current:
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

        if new_game == app().state.game_name:
            return

        _logger.info("Game selection changed.")
        _logger.info("Old = %s, New = %s", app().state.game_name, new_game)

        worker = GameChangeWorker(new_game)
        worker.finished.connect(lambda: self.manager.event_refresh(UIRefreshEvent.GameSelectionChange))

        self._do_work(worker)
