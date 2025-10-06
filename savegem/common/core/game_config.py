import json
import os
import re
from typing import Final

from constants import File
from savegem.common.core.app_data import AppData
from savegem.common.core.save_meta import LocalMetadata, DriveMetadata, MetadataWrapper
from savegem.common.service.gdrive import GDrive
from savegem.common.util.file import delete_file, resolve_app_data
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class GameConfig(AppData):
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
            # Remove token when failed to remove game config.
            # Since there is a chance that user used wrong account to
            # authenticate we remove token so that he could log in again.
            delete_file(resolve_app_data(File.GDriveToken))

            _logger.error(message)
            raise RuntimeError(message)

        game_config.seek(0)
        self.__games_by_name.clear()

        for game in json.load(game_config):
            name = game.get(self.__GAME_NAME)
            local_path = game.get(self.__LOCAL_PATH)
            drive_directory = game.get(self.__PARENT_DIR)
            process_name = game.get(self.__PROCES_NAME)
            allow_auto_mode = game.get(self.__AUTO_MODE_ALLOWED, True)
            files_filter = game.get(self.__FILES_FILTER, [])

            hidden = game.get(self.__HIDDEN, False)
            players = game.get(self.__PLAYERS, [])

            if hidden:
                _logger.debug("Skipping game '%s' since it's marked as hidden.", name)
                continue

            # If players field is not configured it means that everyone
            # has access to the game.
            if len(players) > 0 and self._app.user.email not in players:
                continue

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
        return self.__games_by_name.get(game_name)

    @property
    def names(self):
        """
        Used to get list of game names that are
        available for the user.
        """
        return list(self.__games_by_name.keys())

    def refresh(self):
        """
        Used to reload metadata for all
        registered games.
        """
        for game in self.list:
            game.meta.local.refresh()


class Game:
    """
    Represents a game.
    """

    __SAVE_META_FILE_NAME: Final = "SaveGemMetadata.json"
    __ALL_FILES: Final = ".*"

    def __init__(self,
                 name: str,
                 process_name: str,
                 local_path: str,
                 drive_directory: str,
                 files_filter: list[str],
                 auto_mode_allowed: bool):
        self._name = name
        self.__local_path = local_path
        self.__drive_directory = drive_directory
        self.__files_filter = files_filter
        self._process_name = process_name
        self._auto_mode_allowed = auto_mode_allowed

        self._metadata = MetadataWrapper(LocalMetadata(self), DriveMetadata(self))

    @property
    def name(self):
        """
        Unique name of the game.
        """
        return self._name

    @property
    def process_name(self):
        """
        Name of EXE file of the game
        the way it's displayed in Task Manager.
        """
        return self._process_name

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
    def meta(self):
        """
        Used to get metadata wrapper.

        Contains both metadata of local save
        and metadata of latest save on drive.
        """
        return self._metadata

    @property
    def auto_mode_allowed(self):
        """
        Used to check whether auto mode
        is enabled for the game.
        """
        return self._auto_mode_allowed

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
            patterns.append(self.__ALL_FILES)

        return [re.compile(pattern) for pattern in patterns]

    @property
    def metadata_file_path(self):
        """
        Used to get path to metadata file
        specific to the game.
        """
        return os.path.join(self.local_path, Game.__SAVE_META_FILE_NAME)
