import os.path
import shutil

from constants import ZIP_MIME_TYPE, ZIP_EXTENSION
from src.core import app
from src.service.gdrive import GDrive
from src.service.subscriptable import SubscriptableService, ErrorEvent, DoneEvent, EventKind
from src.util.file import resolve_temp_file, cleanup_directory, save_file
from src.util.logger import get_logger

_logger = get_logger(__name__)


class Downloader(SubscriptableService):
    """
    Used to download latest save files of selected game from Google Drive.
    """

    def download(self):
        """
        Used to download latest save from Google Drive
        also responsible for making backup of old save.
        """

        # 1 - Download last save meta
        # 2 - Download save archive
        # 3 - Save archive in file system
        # 4 - Backup existing save
        # 5 - Extract downloaded archive
        self._set_stages(5)

        saves_directory = app.games.current.local_path
        temp_zip_file_name = resolve_temp_file(f"save.{ZIP_EXTENSION}")

        _logger.debug("savesDirectory = %s", saves_directory)

        if not os.path.exists(saves_directory):
            _logger.error("Directory with saves is missing %s", saves_directory)
            self._send_event(ErrorEvent(EventKind.SAVES_DIRECTORY_IS_MISSING))
            return

        metadata = Downloader.get_last_save_metadata()
        self._complete_stage()

        if metadata is None:
            self._send_event(ErrorEvent(EventKind.LAST_SAVE_METADATA_IS_NONE))
            return

        app.last_save.identifier = metadata.get("name")

        # Download file and write it to zip file locally (in output directory)
        _logger.info("Downloading save archive.")
        file = GDrive.download_file(
            metadata.get("id"),
            subscriber=lambda completion: self._complete_stage(completion)
        ).getvalue()

        _logger.info("Storing file in output directory.")
        save_file(temp_zip_file_name, file, binary=True)
        self._complete_stage()

        # Make backup of existing save, just in case.
        backup_dir = saves_directory + "_backup"
        _logger.debug("backupDirectory = %s", backup_dir)

        # Need to remove directory if it exists since shutil wil create it.
        if os.path.exists(backup_dir):
            _logger.info("Removing backup directory and its contents.")
            cleanup_directory(backup_dir)
            os.removedirs(backup_dir)

        _logger.info("Copying old save to backup directory.")
        shutil.copytree(saves_directory, backup_dir)
        self._complete_stage()

        # Extract archive contents to the target directory
        _logger.info("Extracting archive into saves directory.")
        shutil.unpack_archive(
            temp_zip_file_name,
            saves_directory,
            ZIP_EXTENSION
        )
        self._complete_stage()

        self._send_event(DoneEvent(None))

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

            _logger.error(message)
            raise RuntimeError(message)

        if len(files) == 0:
            _logger.warn("There are no saves on Google Drive for %s.", app.state.game_name)
            return None

        return {
            "id": files[0]["id"],
            "name": files[0]["name"],
            "createdTime": files[0]["createdTime"],
            "owner": files[0]["owners"][0]["displayName"]
        }
