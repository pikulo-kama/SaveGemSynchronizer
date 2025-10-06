import os.path
import shutil
from typing import Final

from constants import ZIP_EXTENSION
from savegem.common.core.game_config import Game
from savegem.common.service.gdrive import GDrive
from savegem.common.service.subscriptable import SubscriptableService, ErrorEvent, DoneEvent, EventKind
from savegem.common.util.file import resolve_temp_file, cleanup_directory, save_file
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class Downloader(SubscriptableService):
    """
    Used to download latest save files of selected game from Google Drive.
    """

    BackupSuffix: Final = "_backup"

    def download(self, game: Game):
        """
        Used to download latest save from Google Drive
        also responsible for making backup of old save.
        """

        # 1 - Download last save meta
        # 2 - Download save archive
        # 3 - Save archive in file system
        # 4 - Backup existing save
        # 5 - Extract downloaded archive
        # 6 - Update in-memory save files metadata.
        self._set_stages(6)

        saves_directory = game.local_path
        temp_zip_file_path = resolve_temp_file(f"save.{ZIP_EXTENSION}")

        _logger.debug("savesDirectory = %s", saves_directory)

        if not os.path.exists(saves_directory):
            _logger.error("Directory with saves is missing %s", saves_directory)
            self._send_event(ErrorEvent(EventKind.SavesDirectoryMissing))
            return

        game.meta.drive.refresh()
        self._complete_stage()

        if not game.meta.drive.is_present:
            self._send_event(ErrorEvent(EventKind.DriveMetadataMissing))
            return

        # Download file and write it to zip file locally (in output directory)
        _logger.info("Downloading save archive.")
        file = GDrive.download_file(
            game.meta.drive.id,
            subscriber=lambda completion: self._complete_stage(completion)
        ).getvalue()

        _logger.info("Storing file in output directory.")
        save_file(temp_zip_file_path, file, binary=True)
        self._complete_stage()

        # Make backup of existing save files, just in case.
        self.__backup_directory(saves_directory)
        self._complete_stage()

        # Extract archive contents to the target directory
        _logger.info("Extracting archive into saves directory.")
        shutil.unpack_archive(
            temp_zip_file_path,
            saves_directory,
            ZIP_EXTENSION
        )
        self._complete_stage()

        # Update metadata in memory.
        game.meta.local.checksum = game.meta.drive.checksum
        self._complete_stage()

        self._send_event(DoneEvent(None))

    @staticmethod
    def __backup_directory(saves_directory: str):
        """
        Used to create backup of provided directory
        will copy directory in the same location and add
        '_backup' suffix.
        """

        # Make backup of existing save, just in case.
        backup_dir = saves_directory + Downloader.BackupSuffix
        _logger.debug("backupDirectory = %s", backup_dir)

        # Need to remove directory if it exists since shutil wil create it.
        if os.path.exists(backup_dir):
            _logger.info("Removing backup directory and its contents.")
            cleanup_directory(backup_dir)
            os.removedirs(backup_dir)

        _logger.info("Copying old save to backup directory.")
        shutil.copytree(saves_directory, backup_dir)
