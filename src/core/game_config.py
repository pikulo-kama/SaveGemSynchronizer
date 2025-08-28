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

    @staticmethod
    def download():
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
        GameConfig.__games = list()
        GameConfig.__games_mapping = dict()

        for game in json.load(game_config):
            name = game["name"]

            if "hidden" in game and game["hidden"] is True:
                logger.info("Skipping game '%s' since it's marked as hidden.", name)
                continue

            GameConfig.__games.append(game)
            GameConfig.__games_mapping[name] = game

        logger.info("Configuration for following game(s) was found = %s", ", ".join(GameConfig.__games_mapping.keys()))

    @staticmethod
    def games():
        """
        Used to get list of game configurations.
        """
        return GameConfig.__games

    @staticmethod
    def game_names():
        return list(GameConfig.__games_mapping.keys())

    @staticmethod
    def local_path():
        """
        Used to get local path where currently selected game save files
        are located.
        """
        return os.path.expandvars(GameConfig.__game_prop("localPath"))

    @staticmethod
    def gdrive_directory_id():
        """
        Used to get Google Drive parent directory ID for currently selected game.
        This directory contain all the save files.
        """
        return GameConfig.__game_prop("gdriveParentDirectoryId")

    @staticmethod
    def __game_prop(property_name: str):
        """
        Used to get property from configuration of game that is in state.
        """

        selected_game = AppState.get_game()

        if selected_game not in GameConfig.__games_mapping:
            selected_game = GameConfig.game_names()[0]
            AppState.set_game(selected_game)

        return GameConfig.__games_mapping[selected_game][property_name]
