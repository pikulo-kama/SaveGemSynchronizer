# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
from savegem.common import initializer
import time
import os.path
import psutil

from constants import File
from savegem.common.service.player import PlayerService
from savegem.common.util.logger import get_logger
from savegem.common.core import app
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import resolve_config, resolve_app_data

_logger = get_logger("watcher")


def _main():
    """
    Watcher service which is used to track running processes
    and send information about which games user currently plays
    to Google Drive activity log file.
    """

    config = JsonConfigHolder(resolve_config(File.ProcessWatcherConfig))
    cleanup_interval = config.get_value("cleanupIntervalSeconds")
    interval = config.get_value("pollingRateSeconds")

    _logger.info("Started process watcher with interval %d second(s).", interval)
    _logger.info("Will remove all data with timestamp older than %d seconds.", cleanup_interval)

    while True:

        # We don't want to trigger authentication flow once user installs
        # application. Once user authenticates thorough UI it will create
        # token file, only then watcher can start doing his job.
        if not os.path.exists(resolve_app_data(File.GDriveToken)):
            time.sleep(interval)
            continue

        try:
            app.user.initialize(GDrive.get_current_user())
            app.games.download()

            active_games = _get_running_games()
            PlayerService.update_activity_data(active_games, cleanup_interval)

        except Exception as error:  # noqa: E722
            _logger.error("Exception in watcher service", error)

        time.sleep(interval)


def _get_running_games():
    """
    Used to get list of game names that are currently running.
    """

    active_games = []
    games_by_processes = {game.process_name.lower(): game.name for game in app.games.get}

    for process in psutil.process_iter(['name']):

        # No need to continue scanning processes if we already
        # found processes for all the games (though it's not very realistic scenario)
        if len(active_games) == len(games_by_processes):
            break

        try:
            process_name = process.name().lower()

            if process_name in games_by_processes.keys():
                game_name = games_by_processes.get(process_name)
                active_games.append(game_name)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return active_games


if __name__ == '__main__':
    _main()
