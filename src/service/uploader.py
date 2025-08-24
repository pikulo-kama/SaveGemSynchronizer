import os
from datetime import datetime
import shutil

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from constants import ZIP_EXTENSION, \
    ZIP_MIME_TYPE, SAVE_VERSION_FILE_NAME, EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.gui.gui_event_listener import trigger_event
from src.service.downloader import Downloader
from src.service.gcloud_service import GCloud
from src.gui.popup.notification import notification
from src.util.file import resolve_temp_file, resolve_app_data


class Uploader:

    def __init__(self):
        from src.gui.gui import GUI

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
        shutil.make_archive(resolve_temp_file(self.__filename), ZIP_EXTENSION, saves_directory)
        media = MediaFileUpload(self.__filepath, mimetype=ZIP_MIME_TYPE)

        try:
            # Upload archive to Google Drive.
            self.__drive.files().create(
                body=metadata,
                media_body=media,
                fields='id'
            ).execute()

        except HttpError as error:
            notification(tr("notification_ErrorUploadingToCloud"))
            print(error)

        # Update last version of save locally.
        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), metadata["name"])

        # Show success notification in application.
        trigger_event(EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, Downloader().get_last_save_metadata())
        notification(tr("notification_SaveHasBeenUploaded"))
