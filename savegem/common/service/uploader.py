import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError

from savegem.common.core import app

from constants import ZIP_EXTENSION
from savegem.common.core.game_config import Game
from savegem.common.core.save_meta import SaveMetaProp
from savegem.common.service.gdrive import GDrive
from savegem.common.service.subscriptable import SubscriptableService, DoneEvent, ErrorEvent, EventKind
from savegem.common.util.file import resolve_temp_file
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class Uploader(SubscriptableService):
    """
    Used to upload current save files of selected game to Google Drive.
    """

    def upload(self, game: Game):
        """
        Used to upload current save files of selected game to Google Drive.
        Save files are being archived before being uploaded.
        """

        # 1 - Create archive target directory to store files for upload
        # 3 - Copy save files to archive target directory
        # 2 - Update metadata and copy to archive target directory
        # 4 - Make archive
        # 5 - Upload archive
        self._set_stages(5)

        saves_root_dir = game.local_path
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d-%H-%M-%S")
        target_archive_path = resolve_temp_file(f"{game.name}-{current_date}")

        if not os.path.exists(saves_root_dir):
            _logger.error("Directory with saves is missing %s", saves_root_dir)
            self._send_event(ErrorEvent(EventKind.SavesDirectoryMissing))
            return

        # Make directory to place all files that needs to be uploaded.
        os.makedirs(target_archive_path)
        self._complete_stage()

        # Copy game files to archive directory.
        for file_path in game.file_list:
            shutil.copy(file_path, target_archive_path)
        self._complete_stage()

        # Set checksum then copy metadata file to target directory.
        game.meta.local.checksum = game.meta.local.calculate_checksum()
        game.meta.local.owner = app.user.name
        game.meta.local.created_time = now.isoformat()

        shutil.copy(game.metadata_file_path, target_archive_path)
        self._complete_stage()

        # Archive save contents to mitigate impact on drive storage.
        _logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(target_archive_path, ZIP_EXTENSION, target_archive_path)
        self._complete_stage()

        archive_props = {
            SaveMetaProp.Owner: app.user.name,
            SaveMetaProp.Checksum: game.meta.local.checksum
            # No need to upload createdTime it would be populated by
            # Google Drive API. We only add it to local metadata for
            # clarity.
        }

        try:
            _logger.info("Uploading archive to cloud.")
            GDrive.upload_file(
                f"{target_archive_path}.{ZIP_EXTENSION}",
                game.drive_directory,
                properties=archive_props,
                subscriber=lambda completion: self._complete_stage(completion)
            )

        except HttpError:
            self._send_event(ErrorEvent(EventKind.ErrorUploadingToDrive))
            return

        self._send_event(DoneEvent(None))
