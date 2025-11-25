import os
import re
import urllib.request
from typing import Final, Iterator

from constants import File, JPG_EXTENSION
from savegem.app.data import holder, HolderObject
from savegem.common.core.app_data import AppData
from savegem.common.core.save_meta import LocalMetadata, DriveMetadata, MetadataWrapper
from savegem.common.db.manager import db
from savegem.common.util.file import delete_file, resolve_resource, resolve_temp_resource, resolve_app_data
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class GameConfig(AppData):
    """
    Used to download and retrieve information from game configuration
    which is stored on Google Drive.
    """

    ParentDir: Final = "gdriveParentDirectoryId"
    FilesFilter: Final = "filesFilter"
    LocalPath: Final = "localPath"
    Players: Final = "players"
    GameName: Final = "name"
    GameLogo: Final = "logo"
    ProcessName: Final = "process"
    Hidden: Final = "hidden"
    AutoModeAllowed: Final = "allowAutoMode"

    def __init__(self, app):
        super().__init__(app)
        self.__games_by_name: dict[str, Game] = dict()

    def __iter__(self) -> Iterator["Game"]:
        return iter(self.__games_by_name.values())

    def initialize(self):
        """
        Used to download game configuration from Google Drive.
        """

        _logger.debug("Downloading game configuration from drive.")
        game_config = holder().get(HolderObject.GamesConfig)

        if game_config is None:
            message = "Configuration file ID is invalid, is missing or you don't have access."
            # Remove token when failed to remove game config.
            # Since there is a chance that user used wrong account to
            # authenticate we remove token so that he could log in again.
            delete_file(resolve_app_data(File.GDriveToken))

            _logger.error(message)
            raise RuntimeError(message)

        self.__games_by_name.clear()

        for game in game_config:
            name = game.get(self.GameName)
            process_name = game.get(self.ProcessName)
            logo = game.get(self.GameLogo)
            local_path = game.get(self.LocalPath)
            drive_directory = game.get(self.ParentDir)
            allow_auto_mode = game.get(self.AutoModeAllowed, True)
            files_filter = game.get(self.FilesFilter, [])

            hidden = game.get(self.Hidden, False)
            players = game.get(self.Players, [])

            if hidden:
                _logger.debug("Skipping game '%s' since it's marked as hidden.", name)
                continue

            # If players field is not configured it means that everyone
            # has access to the game.
            if len(players) > 0 and self.app.users.current.email not in players:
                continue

            self.__games_by_name[name] = Game(
                self,
                name,
                process_name,
                logo,
                local_path,
                drive_directory,
                files_filter,
                allow_auto_mode,
                players
            )

        _logger.debug("Configuration for following game(s) was found = %s", ", ".join(self.names))

    @property
    def empty(self) -> bool:
        """
        Used to get list of game configurations.
        """
        return len(self.__games_by_name) == 0

    @property
    def current(self):
        """
        Used to get currently selected game configuration.
        """
        return self.by_name(self.app.state.game_name)

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
        for game in self:
            game.meta.local.refresh()


class GameSettings:
    """
    Represents game configuration
    controllable by the user.
    """

    def __init__(self, game: "Game", game_config: GameConfig):
        self.__game = game
        self.__settings = self.__get_settings_table(game_config)

    @property
    def auto_mode(self):
        """
        Used to check if auto download/upload mode is enabled.
        """
        return self.__settings.get_first("auto_mode_enabled") == 1

    @auto_mode.setter
    def auto_mode(self, enabled: bool):
        """
        Used to enable/disabled auto mode.
        """

        self.__settings.set_first("auto_mode_enabled", 1 if enabled else 0)
        self.__settings.save()

    def __get_settings_table(self, game_config: GameConfig):
        """
        Used to load game settings from database.
        If there are no settings for the game new
        entry would be created.
        """

        user_id = game_config.app.users.current.id

        settings = db() \
            .table("game_settings") \
            .where("user_id = ? AND game_name = ?", user_id, self.__game.name) \
            .retrieve()

        if len(settings.rows) == 1:
            return settings

        row = settings.add_row()
        settings.set(row, "user_id", user_id)
        settings.set(row, "game_name", self.__game.name)
        settings.save()

        return settings


class Game:
    """
    Represents a game.
    """

    __SAVE_META_FILE_NAME: Final = "SaveGemMetadata.json"
    __ALL_FILES: Final = ".*"

    def __init__(self,
                 game_config: GameConfig,
                 name: str,
                 process_name: str,
                 logo: str,
                 local_path: str,
                 drive_directory: str,
                 files_filter: list[str],
                 auto_mode_allowed: bool,
                 players: list[str]):
        self._name = name
        self._process_name = process_name
        self.__logo = self.__download_logo(logo)
        self.__local_path = local_path
        self.__drive_directory = drive_directory
        self.__files_filter = files_filter
        self._auto_mode_allowed = auto_mode_allowed
        self.__players = players

        self._metadata = MetadataWrapper(LocalMetadata(self), DriveMetadata(self))
        self.__settings = GameSettings(self, game_config)

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
    def logo(self):
        """
        Path to the game logo.
        """
        return self.__logo

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
    def settings(self) -> GameSettings:
        """
        Used to get game settings.
        """
        return self.__settings

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
    def players(self):
        """
        Used to get list of players that have access
        to the game.

        If list is empty it means that all players have
        access.
        """
        return self.__players

    @property
    def metadata_file_path(self):
        """
        Used to get path to metadata file
        specific to the game.
        """
        return os.path.join(self.local_path, Game.__SAVE_META_FILE_NAME)

    def __download_logo(self, logo_url: str):
        """
        Used to download game logo and store it locally.
        Will use default SaveGem logo as fallback value.
        """

        if logo_url is None:
            return resolve_resource("gem.svg")

        logo_path = resolve_temp_resource(f"{self.name}{JPG_EXTENSION}")
        urllib.request.urlretrieve(logo_url, logo_path)

        return logo_path
