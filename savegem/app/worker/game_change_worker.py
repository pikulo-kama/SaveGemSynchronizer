from savegem.app.worker import QWorker, QGUIWorker
from savegem.common.core.context import app


class GameChangeWorker(QGUIWorker):
    """
    Worker used to change currently selected.
    """

    def __init__(self, new_game):
        super().__init__()
        self.__new_game = new_game

    def _run(self):
        app().state.game_name = self.__new_game
        app().activity.refresh()
