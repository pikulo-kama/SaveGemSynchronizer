import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError

from src.core import app
from src.gui import GUI

from constants import ZIP_EXTENSION
from src.core.text_resource import tr
from src.service.gdrive import GDrive
from src.gui.popup.notification import notification
from src.util.file import resolve_temp_file, file_name_from_path, remove_extension_from_path
from src.util.logger import get_logger

_logger = get_logger(__name__)


class Uploader:
    """
    Used to upload current save files of selected game to Google Drive.
    """

    @staticmethod
    def upload():
        """
        Used to upload current save files of selected game to Google Drive.
        Save files are being archived before being uploaded.
        """

        saves_directory = app.games.current.local_path
        file_path = resolve_temp_file(f"save-{datetime.now().strftime("%Y%m%d%H%M%S")}.{ZIP_EXTENSION}")

        if not os.path.exists(saves_directory):
            _logger.error("Directory with saves is missing %s", saves_directory)
            notification(tr("notification_ErrorSaveDirectoryMissing", saves_directory))
            return

        # Archive save contents to mitigate impact on drive storage.
        _logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(remove_extension_from_path(file_path), ZIP_EXTENSION, saves_directory)

        try:
            _logger.info("Uploading archive to cloud.")
            GDrive.upload_file(file_path, app.games.current.drive_directory, subscriber=Uploader.__upload_subscriber)

        except HttpError:
            notification(tr("notification_ErrorUploadingToDrive"))

        # Update last version of save locally.
        app.last_save.identifier = file_name_from_path(file_path)

        # Show success notification in application.
        GUI.instance().refresh()
        notification(tr("notification_SaveHasBeenUploaded"))

    @staticmethod
    def __upload_subscriber(progress):
        GUI.instance().widget("upload_button").configure(text=f"{progress}%")
