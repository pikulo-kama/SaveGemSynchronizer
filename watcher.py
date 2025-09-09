# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer
import time

import psutil

from src.service.player import PlayerService
from src.util.logger import get_logger
from src.core import app
from src.core.json_config_holder import JsonConfigHolder
from src.service.gdrive import GDrive
from src.util.file import resolve_config

_logger = get_logger("watcher")


def _main():
    """
    Watcher service which is used to track running processes
    and send information about which games user currently plays
    to Google Drive activity log file.
    """

    _config = JsonConfigHolder(resolve_config("watcher"))
    cleanup_interval = _config.get_value("cleanupIntervalSeconds")
    interval = _config.get_value("pollingRateSeconds")

    _logger.info("Started process watcher with interval %d second(s).", interval)
    _logger.info("Will remove all data with timestamp older than %d seconds.", cleanup_interval)

    while True:
        app.user.initialize(GDrive.get_current_user())
        app.games.download()
        active_games = []

        for game in app.games.get:
            if _is_running(game.process_name):
                active_games.append(game.name)

        PlayerService.update_activity_data(active_games, cleanup_interval)
        time.sleep(interval)


def _is_running(process_name: str):
    """
    Used to check if process with provided name
    is currently running.
    """

    for process in psutil.process_iter(['name']):
        try:
            if process.name().lower() == process_name.lower():
                return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False


if __name__ == '__main__':
    try:
        _main()

    except Exception as error:  # noqa: E722
        _logger.error("Exception in watcher service:\n%s", error)
