# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
from savegem.common import initializer
from savegem.common.service.daemon import Daemon
from savegem.common.service.downloader import Downloader
from savegem.common.service.player import PlayerService
from savegem.common.service.uploader import Uploader
from savegem.common.core import app
from savegem.common.service.gdrive import GDrive
from savegem.process_watcher.game_process import get_running_game_processes, GameProcess
from savegem.process_watcher.ipc_socket import process_watcher_socket
import threading


class ProcessWatcher(Daemon):
    """
    Process process_watcher.
    Runs in background and checks if any of the configured games is opened.
    Sends information to Google Drive activity log file.
    """

    def __init__(self):
        super().__init__("process_watcher", True)

        self.__downloader = Downloader()
        self.__uploader = Uploader()

    def _work(self):

        app.user.initialize(GDrive.get_current_user())
        app.games.download()

        active_processes = get_running_game_processes()
        # Only get games that are still running, we don't need to show games that has been closed
        # recently in activity log.
        game_names = [process.game.name for process in active_processes if process.is_running]
        PlayerService.update_activity_data(game_names)

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

            # Do not perform anything if auto mode is forcefully
            # disabled for the game in configuration.
            if not process.game.auto_mode_allowed:
                self._logger.debug("Auto mode is disabled for %s", process.game.name)
                continue

            save_meta = Downloader.get_last_save_metadata(process.game)

            drive_checksum = save_meta.get("checksum")
            local_checksum = process.game.calculate_checksum()

            if local_checksum == drive_checksum:
                self._logger.debug(
                    "Skipping upload/download since checksum hasn't changed (%s:%s)",
                    process.game.name,
                    local_checksum
                )
                continue

            if process.has_started:
                self._logger.debug(
                    "Automatically downloading save files for %s since checksum has changed.",
                    process.game.name
                )
                self.__downloader.download(process.game)

            elif process.has_closed:
                self._logger.debug(
                    "Automatically uploading save files for %s since checksum has changed.",
                    process.game.name
                )
                self.__uploader.upload(process.game)


if __name__ == "__main__":
    # Start Process Watcher socket.
    threading.Thread(target=process_watcher_socket.listen, daemon=True).start()
    ProcessWatcher().start()
