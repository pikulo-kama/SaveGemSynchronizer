import os.path
import shutil

from constants import ZIP_MIME_TYPE, ZIP_EXTENSION, SAVE_VERSION_FILE_NAME
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import game_prop
from src.gui.popup.notification import notification
from src.service.GDrive import GDrive
from src.util.file import resolve_temp_file, resolve_app_data, cleanup_directory
from src.gui.gui import GUI
from src.util.logger import get_logger

logger = get_logger(__name__)


class Downloader:
    """
    Used to download latest save files of selected game from Google Drive.
    """

    @staticmethod
    def download():

        saves_directory = os.path.expandvars(game_prop("localPath"))
        temp_zip_file_name = resolve_temp_file(f"save.{ZIP_EXTENSION}")

        metadata = Downloader.get_last_save_metadata()
        logger.debug("savesDirectory = %s", saves_directory)

        if metadata is None:
            notification(tr("label_StorageIsEmpty"))
            return

        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        save_versions.set_value(AppState.get_game(), metadata.get("name"))

        # Download file and write it to zip file locally (in output directory)
        logger.info("Downloading save archive")
        file = GDrive.download_file(metadata.get("id"))

        with open(temp_zip_file_name, "wb") as zip_save:
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
            temp_zip_file_name,
            saves_directory,
            ZIP_EXTENSION
        )

        GUI.instance().refresh()
        notification(tr("notification_NewSaveHasBeenDownloaded"))

    @staticmethod
    def get_last_save_metadata():
        files = GDrive.query_single(
            "files",
            "nextPageToken, files(id, name, owners, createdTime)",
            f"mimeType='{ZIP_MIME_TYPE}' and '{game_prop("gdriveParentDirectoryId")}' in parents"
        )

        if files is None or len(files) == 0:
            logger.warn("There are no files or metadata in Google Drive saves directory.")
            return None

        return {
            "id": files[0]["id"],
            "name": files[0]["name"],
            "createdTime": files[0]["createdTime"],
            "owner": files[0]["owners"][0]["displayName"]
        }
