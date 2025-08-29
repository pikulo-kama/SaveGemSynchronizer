import os.path
import shutil

from constants import ZIP_MIME_TYPE, ZIP_EXTENSION
from src.core import app
from src.core.text_resource import tr
from src.gui.popup.notification import notification
from src.service.gdrive import GDrive
from src.util.file import resolve_temp_file, cleanup_directory, save_file
from src.gui import GUI
from src.util.logger import get_logger

logger = get_logger(__name__)


class Downloader:
    """
    Used to download latest save files of selected game from Google Drive.
    """

    @staticmethod
    def download():
        """
        Used to download latest save from Google Drive
        also responsible for making backup of old save.
        """

        saves_directory = app.games.current.local_path
        temp_zip_file_name = resolve_temp_file(f"save.{ZIP_EXTENSION}")

        if not os.path.exists(saves_directory):
            logger.error("Directory with saves is missing %s", saves_directory)
            notification(tr("notification_ErrorSaveDirectoryMissing", saves_directory))
            return

        metadata = Downloader.get_last_save_metadata()
        logger.debug("savesDirectory = %s", saves_directory)

        if metadata is None:
            notification(tr("label_StorageIsEmpty"))
            return

        app.last_save.identifier = metadata.get("name")

        # Download file and write it to zip file locally (in output directory)
        logger.info("Downloading save archive.")
        file = GDrive.download_file(metadata.get("id"), subscriber=Downloader.__download_subscriber).getvalue()

        logger.info("Storing file in output directory.")
        save_file(temp_zip_file_name, file, binary=True)

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
        """
        Used to get metadata of last save in Google Drive.
        """

        files = GDrive.query_single(
            "files",
            "nextPageToken, files(id, name, owners, createdTime)",
            f"mimeType='{ZIP_MIME_TYPE}' and '{app.games.current.drive_directory}' in parents"
        )

        if files is None:
            message = "Error downloading metadata. Either configuration is incorrect or you don't have access."

            logger.error(message)
            raise RuntimeError(message)

        if len(files) == 0:
            logger.warn("There are no saves on Google Drive for %s.", app.state.game_name)
            return None

        return {
            "id": files[0]["id"],
            "name": files[0]["name"],
            "createdTime": files[0]["createdTime"],
            "owner": files[0]["owners"][0]["displayName"]
        }

    @staticmethod
    def __download_subscriber(progress):
        GUI.instance().widget("download_button").configure(text=f"{progress}%")
