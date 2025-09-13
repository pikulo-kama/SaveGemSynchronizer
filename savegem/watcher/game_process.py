from dataclasses import dataclass
from typing import Final

import psutil
from savegem.common.core import app


_previous_processes = []


def get_running_processes():
    """
    Used to get list of currently opened or recently closed
    games that are configured for the user.
    """

    global _previous_processes

    processes = []
    current_processes = _get_active_game_names()
    all_processes = list(set(_previous_processes + current_processes))

    for process in all_processes:
        status = _ProcessState.Running

        if process in current_processes and process not in _previous_processes:
            status = _ProcessState.Started

        elif process in _previous_processes and process not in current_processes:
            status = _ProcessState.Closed

        processes.append(GameProcess(process, status))

    _previous_processes = current_processes
    return processes


def _get_active_game_names():
    """
    Used to scan running processes
    and return names of game that are currently running.
    """

    game_names = []
    games_by_processes = {game.process_name.lower(): game.name for game in app.games.get}

    for process in psutil.process_iter(['name']):
        # No need to continue scanning processes if we already
        # found processes for all the games (though it's not very realistic scenario)
        if len(game_names) == len(games_by_processes):
            break

        try:
            process_name = process.name().lower()

            if process_name in games_by_processes.keys():
                game_name = games_by_processes.get(process_name)
                game_names.append(game_name)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return game_names


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

    __process_name: str
    __status: str

    @property
    def name(self):
        """
        Name of game that represents process.
        Not process name but name of game how it's
        configured in Google Drive.
        """
        return self.__process_name

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
