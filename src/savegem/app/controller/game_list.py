from typing import Any, Final

from kui.component.button import KamaPushButton
from kui.core.controller import TemplateWidgetController, TemplateWidgetContext
from kui.core.metadata import ControllerArgs
from kutil.logger import get_logger

from savegem.constants import UIRefreshEvent
from savegem.app.worker.game_change_worker import GameChangeWorker
from savegem.common.core.context import context
from savegem.common.core.save_meta import SyncStatus


_logger = get_logger(__name__)


class GameListController(TemplateWidgetController):
    """
    Used to manage game list widget.
    """

    GameOptionSelected: Final = "selected"
    GameOptionWarning: Final = "warning"

    def retrieve_data(self, args: ControllerArgs) -> list[Any]:
        return context().games

    def handle__gameListOption(self, game_button: KamaPushButton, widget_context: TemplateWidgetContext):  # noqa
        """
        Used to link callback to game option and apply
        style properties to it.
        """

        def change_name(game_name: str):
            return lambda: self.__change_game(game_name)

        game_button.clicked.connect(change_name(widget_context.element.name))  # noqa

        if widget_context.element == context().games.current:
            game_button.add_class(self.GameOptionSelected)

        if widget_context.element.meta.sync_status != SyncStatus.UpToDate:
            game_button.add_class(self.GameOptionWarning)

    def resolve(self, widget_context: TemplateWidgetContext, value: str, *args, **kw):
        if value == "name":
            return widget_context.element.name

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

        self.work(worker)
