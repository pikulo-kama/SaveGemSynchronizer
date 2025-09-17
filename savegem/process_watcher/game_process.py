from dataclasses import dataclass
from typing import Final

from savegem.common.core import app
from savegem.common.core.game_config import Game
from savegem.common.util.process import get_running_processes

_previous_game_names = []


def get_running_game_processes():
    """
    Used to get list of currently opened or recently closed
    games that are configured for the user.
    """

    global _previous_game_names

    processes = []
    current_games = _get_active_games()
    current_game_names = [game.name for game in current_games]
    all_game_names = list(set(_previous_game_names + current_game_names))

    for game_name in all_game_names:
        status = _ProcessState.Running

        if game_name in current_games and game_name not in _previous_game_names:
            status = _ProcessState.Started

        elif game_name in _previous_game_names and game_name not in current_game_names:
            status = _ProcessState.Closed

        processes.append(GameProcess(app.games.by_name(game_name), status))

    _previous_game_names = current_game_names
    return processes


def _get_active_games():
    """
    Used to scan running processes
    and return list of games that are currently running.
    """

    games_by_processes = {game.process_name: game for game in app.games.list}
    running_processes = get_running_processes(list(games_by_processes.keys()))

    return [games_by_processes.get(proc.name()) for proc in running_processes]


class _ProcessState:
    """
    Represents enum of process states.
    """

    Running: Final = "RUNNING"
    Started: Final = "STARTED"
    Closed: Final = "CLOSED"


@dataclass
class GameProcess:
    """
    Represents a process.
    """

    __game: Game
    __status: str

    @property
    def game(self) -> Game:
        """
        Game that is related to process.
        """
        return self.__game

    @property
    def is_running(self):
        """
        Used to check if process is running.
        """
        return _ProcessState.Running == self.__status or _ProcessState.Started == self.__status

    @property
    def has_started(self):
        """
        Used to check if process is running and has just been started.
        """
        return _ProcessState.Started == self.__status

    @property
    def has_closed(self):
        """
        Used to check if process has just been closed.
        """
        return _ProcessState.Closed == self.__status
