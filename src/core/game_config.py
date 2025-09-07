import json
import os
import re
from dataclasses import dataclass
from typing import Final

from src.core.app_data import AppData
from src.service.gdrive import GDrive
from src.util.file import resolve_project_data, read_file, save_file
from src.util.logger import get_logger

_logger = get_logger(__name__)


@dataclass
class _Game:
    """
    Represents a game.
    """

    __name: str
    __local_path: str
    __drive_directory: str
    __files_filter: list[str]

    __SAVE_VERSION_FILE_NAME: Final = "SaveGem-SaveVersion.txt"
    __ALL_FILES: Final = ".*"

    @property
    def name(self):
        """
        Unique name of the game.
        """
        return self.__name

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
    def filter_patterns(self):
        """
        Returns list of REGEXP that is used to filter
        save files.
        """

        if len(self.__files_filter) > 0:
            patterns = list(self.__files_filter)
            patterns.append(self.__SAVE_VERSION_FILE_NAME)

        else:
            patterns = [self.__ALL_FILES]

        return [re.compile(pattern) for pattern in patterns]

    @property
    def save_version(self):
        """
        Used to get version of current save file.
        """
        file_path = os.path.join(self.local_path, self.__SAVE_VERSION_FILE_NAME)

        if not os.path.exists(file_path):
            return None

        return read_file(file_path)

    @save_version.setter
    def save_version(self, version):
        """
        Used to store specified version inside save files.
        """
        file_path = str(os.path.join(self.local_path, self.__SAVE_VERSION_FILE_NAME))
        save_file(file_path, version)


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
    __HIDDEN: Final = "hidden"

    def __init__(self):
        super().__init__()
        self.__games_by_name: dict[str, _Game] = dict()

    def download(self):
        """
        Used to download game configuration from Google Drive.
        """

        game_config_pointer_file = resolve_project_data("game-config-file-id.txt")
        game_config_file_id = read_file(game_config_pointer_file)

        _logger.info("Download game configuration from drive.")
        game_config = GDrive.download_file(game_config_file_id)

        if game_config is None:
            message = "Configuration file ID is invalid, is missing or you don't have access."

            _logger.error(message)
            raise RuntimeError(message)

        game_config.seek(0)
        self.__games_by_name.clear()

        for game in json.load(game_config):
            name = game[self.__GAME_NAME]
            local_path = game[self.__LOCAL_PATH]
            drive_directory = game[self.__PARENT_DIR]
            files_filter = []

            if self.__HIDDEN in game and game[self.__HIDDEN] is True:
                _logger.info("Skipping game '%s' since it's marked as hidden.", name)
                continue

            if self.__PLAYERS in game and self._app.user.email not in game[self.__PLAYERS]:
                continue

            if self.__FILES_FILTER in game:
                files_filter = game[self.__FILES_FILTER]

            self.__games_by_name[name] = _Game(name, local_path, drive_directory, files_filter)

        _logger.info("Configuration for following game(s) was found = %s", ", ".join(self.names))

    @property
    def empty(self) -> bool:
        """
        Used to get list of game configurations.
        """
        return len(self.__games_by_name) == 0

    @property
    def names(self):
        """
        Used to get list of game names that are
        available for the user.
        """

        return list(self.__games_by_name.keys())

    @property
    def current(self):
        """
        Used to get currently selected game configuration.
        """
        return self.__games_by_name[self._app.state.game_name]
