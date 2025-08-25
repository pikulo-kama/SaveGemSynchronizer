import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from src.gui.gui import GUI

from constants import ZIP_EXTENSION, ZIP_MIME_TYPE, SAVE_VERSION_FILE_NAME
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.service.GCloud import GCloud
from src.gui.popup.notification import notification
from src.util.file import resolve_temp_file, resolve_app_data
from src.util.logger import get_logger

logger = get_logger(__name__)


class Uploader:

    def __init__(self):
        self.__gui = GUI.instance()
        self.__drive = GCloud().get_drive_service()
        self.__filename = f"save-{datetime.now().strftime("%Y%m%d%H%M%S")}"
        self.__filepath = resolve_temp_file(f"{self.__filename}.{ZIP_EXTENSION}")

    def upload(self):

        saves_directory = os.path.expandvars(game_prop("localPath"))
        cloud_parent_id = game_prop("gcloudParentDirectoryId")

        metadata = {
            "name": f"{self.__filename}.{ZIP_EXTENSION}",
            "parents": [cloud_parent_id]
        }

        # Archive save contents to mitigate impact on drive storage.
        logger.info("Archiving save files that need to be uploaded.")
        shutil.make_archive(resolve_temp_file(self.__filename), ZIP_EXTENSION, saves_directory)
        media = MediaFileUpload(self.__filepath, mimetype=ZIP_MIME_TYPE)

        try:
            # Upload archive to Google Drive.
            logger.info("Uploading archive to cloud.")
            self.__drive.files().create(
                body=metadata,
                media_body=media,
                fields='id'
            ).execute()

        except HttpError as error:
            logger.error("Error uploading archive to cloud", error)
            notification(tr("notification_ErrorUploadingToCloud"))

        # Update last version of save locally.
        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), metadata["name"])

        # Show success notification in application.
        self.__gui.refresh()
        notification(tr("notification_SaveHasBeenUploaded"))
