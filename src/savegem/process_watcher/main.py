from kui.core.app import KamaApplication
from kui.core.shortcut import tr, dynamic_data, add_dynamic_data
from src.savegem.constants import HolderObject
from src.savegem.constants import UIRefreshEvent
from src.savegem.process_watcher.push_notification import push_notification
from src.savegem.app.ipc_socket import ui_socket
from src.savegem.common.core.save_meta import SyncStatus
from src.savegem.common.service.daemon import Daemon
from src.savegem.common.service.downloader import Downloader
from src.savegem.common.service.gdrive import GDrive
from src.savegem.common.service.uploader import Uploader
from src.savegem.common.core.context import context
from src.savegem.process_watcher.game_process import get_running_game_processes, GameProcess
from src.savegem.process_watcher.ipc_socket import process_watcher_socket
import threading


class ProcessWatcher(Daemon):
    """
    Process process_watcher.
    Runs in background and checks if any of the configured games is opened.
    Sends information to Google Drive activity log file.
    """

    def __init__(self):
        Daemon.__init__(self, "process_watcher", True)

        self.__downloader = Downloader()
        self.__uploader = Uploader()

    def _run_once(self):
        add_dynamic_data(HolderObject.CurrentUser, GDrive.get_current_user())
        # No need to get all users that have access since process watcher
        # only needs current user information.
        add_dynamic_data(HolderObject.AllUsers, [dynamic_data(HolderObject.CurrentUser)])
        add_dynamic_data(HolderObject.UserData, GDrive.download_json_file(context().config.users_config_file_id))
        add_dynamic_data(HolderObject.GamesConfig, GDrive.download_json_file(context().config.games_config_file_id))

        context().users.initialize()
        context().games.initialize()
        context().state.refresh()

        application = KamaApplication()
        application.translations.locale = context().state.locale

    def _work(self):
        active_processes = get_running_game_processes()

        # If no new processes started and previous were not closed
        # then there is no point updating activity data or attempting to
        # perform any automatic actions.
        if not any(p.has_started or p.has_closed for p in active_processes):
            return

        game_names = [process.game.name for process in active_processes if not process.has_closed]
        context().activity.update(game_names)

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

            process.game.settings.reload()

            # Only do automatic actions if user enabled auto mode for the game.
            if not process.game.settings.auto_mode:
                self._logger.info("Auto mode is turned OFF for %s", process.game.name)
                continue

            # Do not perform anything if auto mode is forcefully
            # disabled for the game in configuration.
            if not process.game.auto_mode_allowed:
                self._logger.warning("Auto mode is not allowed for %s", process.game.name)
                continue

            process.game.meta.drive.refresh()
            process.game.meta.local.calculate_checksum()

            if process.game.meta.sync_status == SyncStatus.UpToDate:
                self._logger.info(
                    "Skipping upload/download since checksum hasn't changed (%s:%s)",
                    process.game.name,
                    process.game.meta.local.checksum
                )
                continue

            if process.has_started:
                self._logger.info(
                    "Automatically downloading save files for %s since checksum has changed.",
                    process.game.name
                )
                self.__downloader.download(process.game)
                push_notification(tr("notification_NewSaveHasBeenDownloaded"))
                ui_socket.send_ui_refresh_command(UIRefreshEvent.CloudSaveFilesChange)

            elif process.has_closed:
                self._logger.info(
                    "Automatically uploading save files for %s since checksum has changed.",
                    process.game.name
                )
                self.__uploader.upload(process.game)
                push_notification(tr("notification_SaveHasBeenUploaded"))


if __name__ == "__main__":  # pragma: no cover
    # Start Process Watcher socket.
    threading.Thread(target=process_watcher_socket.listen, daemon=True).start()
    ProcessWatcher().start()
