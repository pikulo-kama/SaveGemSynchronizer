import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError

from savegem.common.core import app

from constants import ZIP_EXTENSION
from savegem.common.service.gdrive import GDrive
from savegem.common.service.subscriptable import SubscriptableService, DoneEvent, ErrorEvent, EventKind
from savegem.common.util.file import resolve_temp_file
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class Uploader(SubscriptableService):
    """
    Used to upload current save files of selected game to Google Drive.
    """

    def upload(self):
        """
        Used to upload current save files of selected game to Google Drive.
        Save files are being archived before being uploaded.
        """

        # 1 - Create archive target directory to store files for upload
        # 2 - Set save version in save files
        # 3 - Filter save files and copy them to archive target directory
        # 4 - Make archive
        # 5 - Upload archive
        self._set_stages(5)

        saves_root_dir = app.games.current.local_path
        save_version = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        target_archive_path = resolve_temp_file(f"{app.state.game_name}-{save_version}")

        if not os.path.exists(saves_root_dir):
            _logger.error("Directory with saves is missing %s", saves_root_dir)
            self._send_event(ErrorEvent(EventKind.SAVES_DIRECTORY_IS_MISSING))
            return

        # Make directory to place all files that needs to be uploaded.
        os.makedirs(target_archive_path)
        self._complete_stage()

        # Set save version into archive before uploading it.
        app.games.current.save_version = save_version
        self._complete_stage()

        patterns = app.games.current.filter_patterns

        # Apply filtering to only upload necessary files instead of all.
        for file_name in os.listdir(saves_root_dir):

            if not any(p.match(file_name) for p in patterns):
                continue

            file_path = os.path.join(saves_root_dir, file_name)
            shutil.copy(file_path, target_archive_path)
        self._complete_stage()

        # Archive save contents to mitigate impact on drive storage.
        _logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(target_archive_path, ZIP_EXTENSION, target_archive_path)
        self._complete_stage()

        archive_props = {
            "owner": app.user.name,
            "version": save_version
        }

        try:
            _logger.info("Uploading archive to cloud.")
            GDrive.upload_file(
                f"{target_archive_path}.{ZIP_EXTENSION}",
                app.games.current.drive_directory,
                properties=archive_props,
                subscriber=lambda completion: self._complete_stage(completion)
            )

        except HttpError:
            self._send_event(ErrorEvent(EventKind.ERROR_UPLOADING_TO_DRIVE))
            return

        self._send_event(DoneEvent(None))
