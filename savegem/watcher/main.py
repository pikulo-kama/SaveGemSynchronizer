# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
from savegem.common import initializer
import os.path
from typing import Final

from constants import File
from savegem.common.service.daemon import Daemon
from savegem.common.service.downloader import Downloader
from savegem.common.service.player import PlayerService
from savegem.common.service.uploader import Uploader
from savegem.common.util.logger import get_logger
from savegem.common.core import app
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import resolve_app_data
from savegem.watcher.game_process import get_running_processes, GameProcess

_SERVICE_NAME: Final = "watcher"
_logger: Final = get_logger(_SERVICE_NAME)


class ProcessWatcher(Daemon):
    """
    Process watcher.
    Runs in background and checks if any of the configured games is opened.
    Sends information to Google Drive activity log file.
    """

    __DEFAULT_CLEANUP_INTERVAL: Final = 90

    def __init__(self):
        super().__init__(_SERVICE_NAME)

        self.__cleanup_interval = self.__DEFAULT_CLEANUP_INTERVAL
        self.__downloader = Downloader()
        self.__uploader = Uploader()

    def _initialize(self, config):
        self.__cleanup_interval = config.get_value("logCleanupIntervalSeconds", self.__DEFAULT_CLEANUP_INTERVAL)
        _logger.info("Will remove all data with timestamp older than %d seconds.", self.__cleanup_interval)

    def _work(self):
        # We don't want to trigger authentication flow once user installs
        # application. Once user authenticates thorough UI it will create
        # token file, only then watcher can start doing his job.
        if not os.path.exists(resolve_app_data(File.GDriveToken)):
            _logger.debug("Authentication has not been completed. Sleeping for %d second(s).", self.interval)
            return

        app.user.initialize(GDrive.get_current_user())
        app.games.download()

        active_processes = get_running_processes()
        # Only get games that are still running, we don't need to show games that has been closed
        # recently in activity log.
        game_names = [process.name for process in active_processes if process.is_running]
        PlayerService.update_activity_data(game_names, self.__cleanup_interval)

        if app.state.is_auto_mode:
            self.__perform_automatic_actions(active_processes)

    def __perform_automatic_actions(self, processes: list[GameProcess]):
        """
        Used to perform download/upload of save files when game closes/opens.
        Only works if auto mode is enabled.
        """

        for process in processes:
            # No need to perform extra actions such as metadata download
            # if process is in running state and no action is required.
            if not process.has_started and not process.has_closed:
                continue

            game = app.games.by_name(process.name)

            # Do not perform anything if auto mode is forcefully
            # disabled for the game in configuration.
            if not game.auto_mode_allowed:
                _logger.debug("Auto mode is disabled for %s", game.name)
                continue

            save_meta = Downloader.get_last_save_metadata(game)

            drive_checksum = save_meta.get("checksum")
            local_checksum = game.calculate_checksum()

            if local_checksum == drive_checksum:
                _logger.debug(
                    "Skipping upload/download since checksum hasn't changed (%s:%s)",
                    game.name,
                    local_checksum
                )
                continue

            if process.has_started:
                _logger.debug("Automatically downloading save files for %s since checksum has changed.", game.name)
                self.__downloader.download(game)

            elif process.has_closed:
                _logger.debug("Automatically uploading save files for %s since checksum has changed.", game.name)
                self.__uploader.upload(game)


if __name__ == '__main__':
    ProcessWatcher().start()
