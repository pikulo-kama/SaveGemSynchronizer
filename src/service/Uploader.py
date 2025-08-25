import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError
from src.gui.gui import GUI

from constants import ZIP_EXTENSION, SAVE_VERSION_FILE_NAME
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.service.GDrive import GDrive
from src.gui.popup.notification import notification
from src.util.file import resolve_temp_file, resolve_app_data, file_name_from_path, remove_extension_from_path
from src.util.logger import get_logger

logger = get_logger(__name__)


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

        file_path = resolve_temp_file(f"save-{datetime.now().strftime("%Y%m%d%H%M%S")}.{ZIP_EXTENSION}")
        saves_directory = os.path.expandvars(game_prop("localPath"))
        parent_directory_id = game_prop("gdriveParentDirectoryId")

        if not os.path.exists(saves_directory):
            logger.error("Directory with saves is missing %s", saves_directory)
            notification(tr("notification_ErrorSaveDirectoryMissing", saves_directory))
            return

        # Archive save contents to mitigate impact on drive storage.
        logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(remove_extension_from_path(file_path), ZIP_EXTENSION, saves_directory)

        try:
            GDrive.upload_file(file_path, parent_directory_id)

        except HttpError:
            notification(tr("notification_ErrorUploadingToDrive"))

        # Update last version of save locally.
        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), file_name_from_path(file_path))

        # Show success notification in application.
        GUI.instance().refresh()
        notification(tr("notification_SaveHasBeenUploaded"))
