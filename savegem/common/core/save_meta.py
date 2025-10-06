import abc
import hashlib
from enum import Enum, auto
from typing import Final, TYPE_CHECKING

from constants import ZIP_MIME_TYPE, SHA_256
from savegem.common.core.editable_json_config_holder import EditableJsonConfigHolder
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import file_checksum
from savegem.common.util.logger import get_logger

if TYPE_CHECKING:
    from savegem.common.core.game_config import Game


_logger = get_logger(__name__)


class SyncStatus(Enum):
    """
    Represents save file synchronization status.
    """

    NoInformation = auto()
    LocalOnly = auto()
    NeedsDownload = auto()
    NeedsUpload = auto()
    UpToDate = auto()


class SaveMetaProp:
    """
    Represents collection of metadata properties.
    """

    Owner: Final = "owner"
    CreatedTime: Final = "createdTime"
    Checksum: Final = "checksum"


class MetadataWrapper:
    """
    Holder for both local and drive
    metadata.
    """

    def __init__(self, local: "LocalMetadata", drive: "DriveMetadata"):
        self.__local = local
        self.__drive = drive

    @property
    def local(self):
        """
        Represents local metadata stored
        on user machine.
        """
        return self.__local

    @property
    def drive(self):
        """
        Represents metadata of last save
        available on Google Drive.
        """
        return self.__drive

    @property
    def sync_status(self):
        """
        Used to get current sync status.
        """

        if not self.__drive.is_present:
            return SyncStatus.LocalOnly

        local_save_checksum = self.__local.checksum

        if self.__local.checksum is None:
            return SyncStatus.NoInformation

        current_checksum = self.__local.calculate_checksum()
        drive_save_checksum = self.__drive.checksum

        if local_save_checksum == current_checksum == drive_save_checksum:
            return SyncStatus.UpToDate

        elif local_save_checksum != drive_save_checksum:
            return SyncStatus.NeedsDownload

        elif current_checksum != drive_save_checksum:
            return SyncStatus.NeedsUpload


class Metadata(abc.ABC):  # pragma: no cover
    """
    Represents game save metadata.
    """

    def __init__(self, game: "Game"):
        self._game = game

    @property
    @abc.abstractmethod
    def owner(self):
        """
        Used to get owner of save.
        Name of person that created save.
        """
        pass

    @property
    @abc.abstractmethod
    def created_time(self):
        """
        Used to get date when save was uploaded.
        """
        pass

    @property
    @abc.abstractmethod
    def checksum(self):
        """
        Used to get checksum of save.
        """
        pass

    @abc.abstractmethod
    def refresh(self):
        """
        Used to refresh save metadata.
        """
        pass


class LocalMetadata(Metadata):

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.__metadata = EditableJsonConfigHolder(self._game.metadata_file_path)

    @property
    def owner(self):
        return self.__metadata.get_value(SaveMetaProp.Owner)

    @property
    def created_time(self):
        return self.__metadata.get_value(SaveMetaProp.CreatedTime)

    @property
    def checksum(self):
        return self.__metadata.get_value(SaveMetaProp.Checksum)

    @owner.setter
    def owner(self, owner: str):
        self.__metadata.set_value(SaveMetaProp.Owner, owner)

    @created_time.setter
    def created_time(self, created_time: str):
        self.__metadata.set_value(SaveMetaProp.CreatedTime, created_time)

    @checksum.setter
    def checksum(self, checksum: str):
        self.__metadata.set_value(SaveMetaProp.Checksum, checksum)

    def calculate_checksum(self):
        """
        Used to calculate checksum of save files.
        """

        checksum = hashlib.new(SHA_256)

        for file_path in self._game.file_list:
            # Don't include metadata when calculating checksum.
            if file_path == self._game.metadata_file_path:
                continue

            checksum.update(file_checksum(file_path).encode())

        return checksum.hexdigest()

    def refresh(self):
        self.__metadata = EditableJsonConfigHolder(self._game.metadata_file_path)


class DriveMetadata(Metadata):

    __ID_PROP: Final = "id"

    def __init__(self, game: "Game"):
        super().__init__(game)

        self.__id = None
        self.__owner = None
        self.__created_time = None
        self.__checksum = None

        self.__is_present = False

    @property
    def is_present(self):
        return self.__is_present

    @property
    def id(self):
        return self.__id

    @property
    def owner(self):
        return self.__owner

    @property
    def created_time(self):
        return self.__created_time

    @property
    def checksum(self):
        return self.__checksum

    def refresh(self):
        """
        Used to download latest save
        metadata from Google Drive.
        """

        metadata = GDrive.query_single(
            f"mimeType='{ZIP_MIME_TYPE}' and '{self._game.drive_directory}' in parents and trashed=false",
            "files(id, appProperties, createdTime)"
        )

        if metadata is None:
            message = "Error downloading metadata. Either configuration is incorrect or you don't have access."

            _logger.error(message)
            raise RuntimeError(message)

        files_meta = metadata.get("files")

        if len(files_meta) == 0:
            _logger.warning("There are no saves on Google Drive for %s.", self._game.name)
            self.__is_present = False
            return

        file_meta = files_meta[0]
        properties = file_meta.get("appProperties") or {}

        self.__id = file_meta.get(self.__ID_PROP)
        self.__owner = properties.get(SaveMetaProp.Owner)
        self.__created_time = file_meta.get(SaveMetaProp.CreatedTime)
        self.__checksum = properties.get(SaveMetaProp.Checksum)

        self.__is_present = True
