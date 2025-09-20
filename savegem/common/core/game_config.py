import hashlib
import json
import os
import re
from typing import Final

from savegem.common.core.app_data import AppData
from savegem.common.core.editable_json_config_holder import EditableJsonConfigHolder
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import file_checksum
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class Game:
    """
    Represents a game.
    """

    __SAVE_META_FILE_NAME: Final = "SaveGemMetadata.json"
    __ALL_FILES: Final = ".*"

    __META_CHECKSUM_ATTR = "checksum"

    def __init__(self,
                 name: str,
                 process_name: str,
                 local_path: str,
                 drive_directory: str,
                 files_filter: list[str],
                 auto_mode_allowed: bool):
        self.__name = name
        self.__local_path = local_path
        self.__drive_directory = drive_directory
        self.__files_filter = files_filter
        self.__process_name = process_name
        self.__auto_mode_allowed = auto_mode_allowed

        self.__metadata = EditableJsonConfigHolder(self.metadata_file_path)

    @property
    def name(self):
        """
        Unique name of the game.
        """
        return self.__name

    @property
    def process_name(self):
        """
        Name of EXE file of the game
        the way it's displayed in Task Manager.
        """
        return self.__process_name

    @property
    def local_path(self):
        """
        Path to the game on local filesystem.
        """
        return os.path.expandvars(self.__local_path)

    @property
    def drive_directory(self):
        """
        ID of Google Drive directory where save files located
        """
        return self.__drive_directory

    @property
    def auto_mode_allowed(self):
        return self.__auto_mode_allowed

    @property
    def file_list(self):
        """
        Used to get list of save file paths
        that are being managed for game.
        """

        save_directory = self.local_path

        for file_name in sorted(os.listdir(save_directory)):
            # Only include files that are present in game config.
            if any(p.match(file_name) for p in self.filter_patterns):
                yield os.path.join(save_directory, file_name)

    @property
    def filter_patterns(self):
        """
        Returns list of REGEXP that is used to filter
        save files.
        """

        patterns = list(self.__files_filter)

        if len(patterns) == 0:
            patterns = [self.__ALL_FILES]

        return [re.compile(pattern) for pattern in patterns]

    @property
    def checksum(self):
        """
        Used to get checksum of save files store in metadata file.
        """
        return self.__metadata.get_value(self.__META_CHECKSUM_ATTR)

    @checksum.setter
    def checksum(self, checksum):
        """
        Used to set checksum of save files inside metadata file.
        """
        self.__metadata.set_value(self.__META_CHECKSUM_ATTR, checksum)

    def calculate_checksum(self):
        """
        Used to calculate checksum of save files.
        """

        checksum = hashlib.new("sha256")

        for file_path in self.file_list:

            # Don't include metadata when calculating checksum.
            if file_path == self.metadata_file_path:
                continue

            checksum.update(file_checksum(file_path).encode())

        return checksum.hexdigest()

    def reload_metadata(self):
        """
        Used to read metadata file in case
        it was updated by another process.
        """
        self.__metadata = EditableJsonConfigHolder(self.metadata_file_path)

    @property
    def metadata_file_path(self):
        """
        Used to get path to metadata file
        specific to the game.
        """

        return os.path.join(self.local_path, Game.__SAVE_META_FILE_NAME)


class _GameConfig(AppData):
    """
    Used to download and retrieve information from game configuration
    which is stored on Google Drive.
    """

    __PARENT_DIR: Final = "gdriveParentDirectoryId"
    __FILES_FILTER: Final = "filesFilter"
    __LOCAL_PATH: Final = "localPath"
    __PLAYERS: Final = "players"
    __GAME_NAME: Final = "name"
    __PROCES_NAME: Final = "process"
    __HIDDEN: Final = "hidden"
    __AUTO_MODE_ALLOWED: Final = "allowAutoMode"

    def __init__(self):
        super().__init__()
        self.__games_by_name: dict[str, Game] = dict()

    def download(self):
        """
        Used to download game configuration from Google Drive.
        """

        _logger.debug("Downloading game configuration from drive.")
        game_config = GDrive.download_file(self._app.config.games_config_file_id)

        if game_config is None:
            message = "Configuration file ID is invalid, is missing or you don't have access."

            _logger.error(message)
            raise RuntimeError(message)

        game_config.seek(0)
        self.__games_by_name.clear()

        for game in json.load(game_config):
            name = game.get(self.__GAME_NAME)
            local_path = game.get(self.__LOCAL_PATH)
            drive_directory = game.get(self.__PARENT_DIR)
            process_name = game.get(self.__PROCES_NAME)
            allow_auto_mode = True
            files_filter = []

            if self.__HIDDEN in game and game.get(self.__HIDDEN) is True:
                _logger.debug("Skipping game '%s' since it's marked as hidden.", name)
                continue

            if self.__PLAYERS in game and self._app.user.email not in game.get(self.__PLAYERS):
                continue

            if self.__AUTO_MODE_ALLOWED in game:
                allow_auto_mode = game.get(self.__AUTO_MODE_ALLOWED)

            if self.__FILES_FILTER in game:
                files_filter = game.get(self.__FILES_FILTER)

            self.__games_by_name[name] = Game(
                name,
                process_name,
                local_path,
                drive_directory,
                files_filter,
                allow_auto_mode
            )

        _logger.debug("Configuration for following game(s) was found = %s", ", ".join(self.names))

    @property
    def empty(self) -> bool:
        """
        Used to get list of game configurations.
        """
        return len(self.__games_by_name) == 0

    @property
    def list(self):
        """
        Used to return list of all games currently
        registered in application.
        """
        return list(self.__games_by_name.values())

    @property
    def current(self):
        """
        Used to get currently selected game configuration.
        """
        return self.by_name(self._app.state.game_name)

    def by_name(self, game_name: str):
        """
        Used to get game by its name.
        """
        return self.__games_by_name[game_name]

    @property
    def names(self):
        """
        Used to get list of game names that are
        available for the user.
        """
        return list(self.__games_by_name.keys())

    def reload(self):
        """
        Used to reload metadata for all
        registered games.
        """

        for game in self.list:
            game.reload_metadata()
