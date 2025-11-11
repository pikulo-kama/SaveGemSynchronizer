import abc
import hashlib
from enum import Enum, auto
from typing import Final, TYPE_CHECKING, Iterator

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
    Size: Final = "size"


class MetadataWrapper:
    """
    Holder for both local and drive
    metadata.
    """

    def __init__(self, local: "LocalMetadata", drive: "DriveMetadata"):
        self.__local = local
        self.__drive = drive
        self.__sync_status: SyncStatus = SyncStatus.NoInformation

    @property
    def local(self) -> "LocalMetadata":
        """
        Represents local metadata stored
        on user machine.
        """
        return self.__local

    @property
    def drive(self) -> "DriveMetadata":
        """
        Represents metadata of last save
        available on Google Drive.
        """
        return self.__drive

    @property
    def sync_status(self) -> SyncStatus:
        """
        Used to get current sync status.
        """

        if not self.__drive.is_present:
            return SyncStatus.LocalOnly

        local_save_checksum = self.__local.checksum

        if self.__local.checksum is None:
            return SyncStatus.NoInformation

        current_checksum = self.__local.current_checksum
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
    def owner(self) -> str:
        """
        Used to get owner of save.
        Name of person that created save.
        """
        pass

    @property
    @abc.abstractmethod
    def created_time(self) -> str:
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
    """
    Used to hold metadata of local save on user machine.
    """

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.__metadata = EditableJsonConfigHolder(self._game.metadata_file_path)
        self.__current_checksum = None

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

    @property
    def current_checksum(self):
        """
        Used to get current checksum of save files.
        This doesn't use checksum of save metadata in case it
        was downloaded.
        """
        return self.__current_checksum

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

        self.__current_checksum = checksum.hexdigest()
        return self.__current_checksum

    def refresh(self):
        self.__metadata = EditableJsonConfigHolder(self._game.metadata_file_path)


class DriveFileMetadata(Metadata):
    """
    Used to hold metadata of single save on drive.
    """

    def __init__(self, game: "Game", file_id: str, owner: str, created_time: str, checksum: str, size: int):
        super().__init__(game)

        self.__id = file_id
        self.__owner = owner
        self.__created_time = created_time
        self.__checksum = checksum
        self.__size = size

    @property
    def id(self):
        """
        Used to get ID of save on drive.
        """
        return self.__id

    @property
    def owner(self):
        """
        Used to get owner of save.
        """
        return self.__owner

    @property
    def created_time(self):
        """
        Used to get date when save was uploaded.
        """
        return self.__created_time

    @property
    def checksum(self):
        """
        Used to get checksum of save.
        """
        return self.__checksum

    @property
    def size(self):
        """
        Used to get size of save.
        """
        return self.__size

    def refresh(self):
        pass


class DriveMetadata(Metadata):
    """
    Holds metadata of all save files in drive.
    """

    __ID_PROP: Final = "id"

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.__files_metadata: list[DriveFileMetadata] = []

        self.refresh()

    def __iter__(self) -> Iterator[DriveFileMetadata]:
        return iter(self.__files_metadata)

    @property
    def is_present(self):
        """
        Used to check if there are saves in cloud.
        """
        return len(self.__files_metadata) > 0

    @property
    def latest(self):
        """
        Used to get metadata of latest upload save.
        """
        return self.__files_metadata[0]

    def by_id(self, file_id: str):
        """
        Used to get metadata of specific save.
        """
        return next(meta for meta in self.__files_metadata if meta.id == file_id)

    @property
    def id(self):
        """
        Used to get ID of latest save on drive.
        """
        return self.latest.id

    @property
    def owner(self):
        """
        Used to get owner of latest save on drive.
        """
        return self.latest.owner

    @property
    def created_time(self):
        """
        Used to get date when latest save was uploaded to drive.
        """
        return self.latest.created_time

    @property
    def checksum(self):
        """
        Used to get checksum of latest save.
        """
        return self.latest.checksum

    @property
    def size(self):
        """
        Used to get size of latest save.
        """
        return self.latest.size

    def refresh(self):
        """
        Used to download latest save
        metadata from Google Drive.
        """

        self.__files_metadata.clear()

        metadata = GDrive.query_metadata(
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
            return

        for file_meta in files_meta:
            properties = file_meta.get("appProperties") or {}

            file_metadata = DriveFileMetadata(
                game=self._game,
                file_id=file_meta.get(self.__ID_PROP),
                owner=properties.get(SaveMetaProp.Owner),
                created_time=file_meta.get(SaveMetaProp.CreatedTime),
                checksum=properties.get(SaveMetaProp.Checksum),
                size=int(properties.get(SaveMetaProp.Size, -1))
            )

            self.__files_metadata.append(file_metadata)
