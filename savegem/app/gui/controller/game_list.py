from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.list import QScrollableWidget
from savegem.app.gui.component.spacer import QSpacer
from savegem.app.gui.constants import UIRefreshEvent, QBool
from savegem.app.gui.controller import WidgetController
from savegem.app.worker.game_change_worker import GameChangeWorker
from savegem.common.core.context import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class GameListController(WidgetController):
    """
    Used to control list of currently available games.
    """

    def refresh(self, game_list: QScrollableWidget):

        # Ideally this creation of games should happen
        # through metadata but since game list is dynamic,
        # and we also only build widgets in setup section
        # it's not the easiest thing to do. Because of that
        # at the moment games are being recreated manually
        # each time widget is being refreshed.

        def change_name(game_name: str):
            return lambda: self.__change_game(game_name)

        self.manager.remove_child_widgets(game_list)

        for game in app().games:
            game_button = QCustomPushButton()
            game_button.setObjectName("gameListOption")
            game_button.setText(game.name)
            game_button.clicked.connect(change_name(game.name))  # noqa

            if game == app().games.current:
                game_button.setProperty("selected", QBool(True))

            if game.meta.sync_status != SyncStatus.UpToDate:
                game_button.setProperty("warning", QBool(True))

            game_list.layout().add_dynamic_widget(game_button)

        game_list.layout().add_dynamic_widget(QSpacer())

    def __change_game(self, new_game):
        """
        Used to change currently selected game.
        """

        if new_game == app().state.game_name:
            return

        _logger.info("Game selection changed.")
        _logger.info("Selected game - %s", new_game)

        worker = GameChangeWorker(new_game)
        worker.finished.connect(lambda: self.manager.gui.refresh(UIRefreshEvent.GameSelectionChange))

        self._do_work(worker)
