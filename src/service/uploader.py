import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError

from src.core import app

from constants import ZIP_EXTENSION
from src.service.gdrive import GDrive
from src.service.subscriptable import SubscriptableService, DoneEvent, ErrorEvent, EventKind
from src.util.file import resolve_temp_file, remove_extension_from_path
from src.util.logger import get_logger

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

        # 1 - Archive
        # 2 - Set save version
        # 3 - Upload
        self._set_stages(3)

        saves_directory = app.games.current.local_path
        save_version = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_path = resolve_temp_file(f"save-{save_version}.{ZIP_EXTENSION}")

        if not os.path.exists(saves_directory):
            _logger.error("Directory with saves is missing %s", saves_directory)
            self._send_event(ErrorEvent(EventKind.SAVES_DIRECTORY_IS_MISSING))
            return

        # Set save version into archive before uploading it.
        app.games.current.save_version = save_version
        self._complete_stage()

        # Archive save contents to mitigate impact on drive storage.
        _logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(remove_extension_from_path(file_path), ZIP_EXTENSION, saves_directory)
        self._complete_stage()

        try:
            _logger.info("Uploading archive to cloud.")
            GDrive.upload_file(
                file_path,
                app.games.current.drive_directory,
                subscriber=lambda completion: self._complete_stage(completion)
            )

        except HttpError:
            self._send_event(ErrorEvent(EventKind.ERROR_UPLOADING_TO_DRIVE))
            return

        self._send_event(DoneEvent(None))
