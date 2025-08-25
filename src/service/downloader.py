import os.path
import shutil

from googleapiclient.errors import HttpError

from constants import ZIP_MIME_TYPE, ZIP_EXTENSION, SAVE_VERSION_FILE_NAME
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.gui.popup.notification import notification
from src.service.gcloud_service import GCloud
from src.util.file import resolve_temp_file, resolve_app_data, cleanup_directory
from src.gui.gui import GUI
from src.util.logger import get_logger

logger = get_logger(__name__)


class Downloader:

    def __init__(self):
        self.__gui = GUI.instance()
        self.__drive = GCloud().get_drive_service()
        self.__tmp_zip_file = resolve_temp_file(f'save.{ZIP_EXTENSION}')

    def download(self):

        saves_directory = os.path.expandvars(game_prop("localPath"))
        metadata = self.get_last_save_metadata()
        logger.debug("savesDirectory = %s", saves_directory)

        if metadata is None:
            notification(tr("notification_StorageIsEmpty"))
            return

        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), metadata.get("name"))

        # Download file and write it to zip file locally (in output directory)
        logger.info("Downloading save archive")
        file = GCloud().download_file(metadata.get("id"))

        with open(self.__tmp_zip_file, "wb") as zip_save:
            logger.info("Storing file in output directory.")
            zip_save.write(file)

        # Make backup of existing save, just in case.
        backup_dir = saves_directory + "_backup"
        logger.debug("backupDirectory = %s", backup_dir)

        # Need to remove directory if it exists since shutil wil create it.
        if os.path.exists(backup_dir):
            logger.info("Removing backup directory and its contents.")
            cleanup_directory(backup_dir)
            os.removedirs(backup_dir)

        logger.info("Copying old save to backup directory.")
        shutil.copytree(saves_directory, backup_dir)

        # Extract archive contents to the target directory
        logger.info("Extracting archive into saves directory.")
        shutil.unpack_archive(
            self.__tmp_zip_file,
            saves_directory,
            ZIP_EXTENSION
        )

        self.__gui.refresh()
        notification(tr("notification_NewSaveHasBeenDownloaded"))

    def get_last_save_metadata(self):

        files = []

        try:
            response = self.__drive.files().list(
                q=f"mimeType='{ZIP_MIME_TYPE}' and '{game_prop("gcloudParentDirectoryId")}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name, owners, createdTime)',
                pageToken=None,
                pageSize=1
            ).execute()

            files = response.get("files", [])

        except HttpError as e:
            logger.error("Error downloading save metadata", e)

        if len(files) == 0:
            logger.warn("There are no files or metadata in cloud saves directory.")
            return None

        return {
            "id": files[0]["id"],
            "name": files[0]["name"],
            "createdTime": files[0]["createdTime"],
            "owner": files[0]["owners"][0]["displayName"],
        }
