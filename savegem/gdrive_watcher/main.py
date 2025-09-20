from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.ipc_socket import ui_socket
from savegem.common.core import app
from constants import File
import threading
import os.path

from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.service.daemon import Daemon
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import resolve_temp_file
from savegem.gdrive_watcher.ipc_socket import google_drive_watcher_socket


class GDriveWatcher(Daemon):

    def __init__(self):
        self.__start_page_token = None
        super().__init__("gdrive_watcher", True)

    def _work(self):
        """
        Used to poll from Google Drive Changes API
        and check whether UI dependent files have been updated.
        """

        # Google Drive watcher service should only work when GUI is running
        # since otherwise it would be doing extra work by polling Google Drive
        # API as well as will constantly send data to non-existing socket.
        if not os.path.exists(resolve_temp_file(File.GUIInitializedFlag)):
            return

        app.user.initialize(GDrive.get_current_user)
        app.games.download()

        files, directories = self.__get_changes()
        save_files_modified = app.games.current.drive_directory in directories
        games_config_modified = app.config.games_config_file_id in files
        activity_log_modified = app.config.activity_log_file_id in files

        self._logger.debug("Current game files modified: %s", save_files_modified)
        self._logger.debug("Games config modified: %s", games_config_modified)
        self._logger.debug("Activity log modified: %s", activity_log_modified)

        if save_files_modified:
            self.__send_refresh_event(UIRefreshEvent.CloudSaveFilesChange)

        if games_config_modified:
            self.__send_refresh_event(UIRefreshEvent.GameConfigChange)

        if activity_log_modified:
            self.__send_refresh_event(UIRefreshEvent.ActivityLogUpdate)

    def __get_changes(self):
        """
        Used to get formatted changes from Google Drive Changes API.
        """

        response = GDrive.get_changes(self.__start_page_token)
        self.__start_page_token = response.get("newStartPageToken")

        modified_files = []
        affected_directories = []

        changes = response.get("changes", [])
        self._logger.debug("changes=%s", changes)
        self._logger.debug("startPageToken=%s", self.__start_page_token)

        for change in changes:
            file = change.get("file")
            is_removed = change.get("removed", False)

            # This is a hack to make a workaround for
            # Google Drive "genius" logic of not providing any information
            # about what was removed on cloud. To be safe if something is removed
            # on drive we will assume it was for current game and refresh UI.
            if is_removed:
                affected_directories.append(app.games.current.drive_directory)
                continue

            modified_files.append(file.get("id"))
            affected_directories.append(file.get("parents")[0])

        self._logger.debug("modified_files=%s", modified_files)
        self._logger.debug("affected_directories=%s", affected_directories)

        return modified_files, affected_directories

    def __send_refresh_event(self, event):
        """
        Used to send refresh command to GUI application.
        """

        self._logger.debug("Sending RefreshUI command with event='%s'", event)
        ui_socket.send({
            "command": IPCCommand.RefreshUI,
            "event": event
        })


if __name__ == "__main__":
    # Start Google Drive Watcher socket.
    threading.Thread(target=google_drive_watcher_socket.listen, daemon=True).start()
    GDriveWatcher().start()
