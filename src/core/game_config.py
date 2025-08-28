import json
import os

from constants import GAME_CONFIG_POINTER_FILE_NAME
from src.core.app_state import AppState
from src.service.gdrive import GDrive
from src.util.file import resolve_project_data, read_file
from src.util.logger import get_logger

logger = get_logger(__name__)


class GameConfig:
    """
    Used to download and retrieve information from game configuration
    which is stored on Google Drive.
    """

    __games: list = list()
    __games_mapping: dict = dict()

    __GAME_NAME = "name"
    __LOCAL_PATH = "localPath"
    __PARENT_DIR = "gdriveParentDirectoryId"
    __HIDDEN = "hidden"
    __PLAYERS = "players"

    @classmethod
    def download(cls):
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
        cls.__games = list()
        cls.__games_mapping = dict()

        user_email = AppState.get_user_email()

        for game in json.load(game_config):
            name = game[cls.__GAME_NAME]

            if cls.__HIDDEN in game and game[cls.__HIDDEN] is True:
                logger.info("Skipping game '%s' since it's marked as hidden.", name)
                continue

            if cls.__PLAYERS in game and user_email not in game[cls.__PLAYERS]:
                continue

            cls.__games.append(game)
            cls.__games_mapping[name] = game

        logger.info("Configuration for following game(s) was found = %s", ", ".join(cls.__games_mapping.keys()))

    @classmethod
    def games(cls):
        """
        Used to get list of game configurations.
        """
        return cls.__games

    @classmethod
    def game_names(cls):
        return list(cls.__games_mapping.keys())

    @classmethod
    def local_path(cls):
        """
        Used to get local path where currently selected game save files
        are located.
        """
        return os.path.expandvars(cls.__game_prop(cls.__LOCAL_PATH))

    @classmethod
    def gdrive_directory_id(cls):
        """
        Used to get Google Drive parent directory ID for currently selected game.
        This directory contain all the save files.
        """
        return cls.__game_prop(cls.__PARENT_DIR)

    @classmethod
    def __game_prop(cls, property_name: str):
        """
        Used to get property from configuration of game that is in state.
        """

        selected_game = AppState.get_game()

        if selected_game not in cls.__games_mapping:
            selected_game = cls.game_names()[0]
            AppState.set_game(selected_game)

        return cls.__games_mapping[selected_game][property_name]
