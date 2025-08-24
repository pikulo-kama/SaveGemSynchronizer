import os.path
import shutil

from constants import ZIP_MIME_TYPE, ZIP_EXTENSION, SAVE_VERSION_FILE_NAME, EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.gui.gui_event_listener import trigger_event
from src.gui.popup.notification import notification
from src.service.gcloud_service import GCloud
from src.util.file import resolve_temp_file, resolve_app_data, cleanup_directory
from src.gui.gui import GUI


class Downloader:

    def __init__(self):
        self.__gui = GUI.instance()
        self.__drive = GCloud().get_drive_service()
        self.__tmp_zip_file = resolve_temp_file(f'save.{ZIP_EXTENSION}')

    def download(self):

        saves_directory = os.path.expandvars(game_prop("localPath"))
        metadata = self.get_last_save_metadata()

        if metadata is None:
            notification(tr("notification_StorageIsEmpty"))
            return

        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), metadata.get("name"))

        # Download file and write it to zip file locally (in output directory)
        file = GCloud().download_file(metadata.get("id"))
        with open(self.__tmp_zip_file, "wb") as zip_save:
            zip_save.write(file)

        # Make backup of existing save, just in case.
        backup_dir = saves_directory + "_backup"

        # Need to remove directory if it exists since shutil wil create it.
        if os.path.exists(backup_dir):
            cleanup_directory(backup_dir)
            os.removedirs(backup_dir)

        shutil.copytree(saves_directory, backup_dir)

        # Extract archive contents to the target directory
        shutil.unpack_archive(
            self.__tmp_zip_file,
            saves_directory,
            ZIP_EXTENSION
        )

        trigger_event(EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, self.get_last_save_metadata())
        notification(tr("notification_NewSaveHasBeenDownloaded"))

    def get_last_save_metadata(self):

        response = self.__drive.files().list(
            q=f"mimeType='{ZIP_MIME_TYPE}' and '{game_prop("gcloudParentDirectoryId")}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, owners, createdTime)',
            pageToken=None,
            pageSize=1
        ).execute()

        files = response.get("files", [])

        if len(files) == 0:
            return None

        return {
            "id": files[0]["id"],
            "name": files[0]["name"],
            "createdTime": files[0]["createdTime"],
            "owner": files[0]["owners"][0]["displayName"],
        }
