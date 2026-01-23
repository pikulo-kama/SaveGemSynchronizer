from kui.core.worker import KamaWorker
from src.savegem.common.core.context import context


class GameChangeWorker(KamaWorker):
    """
    Worker used to change currently selected.
    """

    def __init__(self, new_game):
        super().__init__()
        self.__new_game = new_game

    def _run(self):
        context().state.game_name = self.__new_game
        context().activity.refresh()
