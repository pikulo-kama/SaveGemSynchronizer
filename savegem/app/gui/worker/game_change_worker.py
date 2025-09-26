from savegem.app.gui.worker import QWorker
from savegem.common.core import app


class GameChangeWorker(QWorker):
    """
    Worker used to change currently selected.
    """

    def __init__(self, new_game):
        super().__init__()
        self.__new_game = new_game

    def _run(self):
        app.state.game_name = self.__new_game
        app.games.current.meta.drive.refresh()
        app.activity.refresh()
