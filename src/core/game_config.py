import json
import os
from dataclasses import dataclass

from constants import GAME_CONFIG_POINTER_FILE_NAME
from src.core.app_data import AppData
from src.service.gdrive import GDrive
from src.util.file import resolve_project_data, read_file
from src.util.logger import get_logger

logger = get_logger(__name__)


_GAME_NAME = "name"
_LOCAL_PATH = "localPath"
_PARENT_DIR = "gdriveParentDirectoryId"
_HIDDEN = "hidden"
_PLAYERS = "players"


@dataclass
class _Game:
    """
    Represents a game.
    """

    _name: str
    _local_path: str
    _drive_directory: str

    @property
    def name(self):
        """
        Unique name of the game.
        """
        return self._name

    @property
    def local_path(self):
        """
        Path to the game on local filesystem.
        """
        return os.path.expandvars(self._local_path)

    @property
    def drive_directory(self):
        """
        ID of Google Drive directory where save files located
        """
        return self._drive_directory


class _GameConfig(AppData):
    """
    Used to download and retrieve information from game configuration
    which is stored on Google Drive.
    """

    def __init__(self):
        super().__init__()
        self.__games_by_name: dict[str, _Game] = dict()

    def download(self):
        """
        Used to download game configuration from Google Drive.
        """

        game_config_pointer_file = resolve_project_data(GAME_CONFIG_POINTER_FILE_NAME)
        game_config_file_id = read_file(game_config_pointer_file)

        logger.info("Download game configuration from drive.")
        game_config = GDrive.download_file(game_config_file_id)

        if game_config is None:
            message = "Configuration file ID is invalid, is missing or you don't have access."

            logger.error(message)
            raise RuntimeError(message)

        game_config.seek(0)
        self.__games_by_name.clear()

        for game in json.load(game_config):
            name = game[_GAME_NAME]
            local_path = game[_LOCAL_PATH]
            drive_directory = game[_PARENT_DIR]

            if _HIDDEN in game and game[_HIDDEN] is True:
                logger.info("Skipping game '%s' since it's marked as hidden.", name)
                continue

            if _PLAYERS in game and self._app.state.user_email not in game[_PLAYERS]:
                continue

            self.__games_by_name[name] = _Game(name, local_path, drive_directory)

        logger.info("Configuration for following game(s) was found = %s", ", ".join(self.names))

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
