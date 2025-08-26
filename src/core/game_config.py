import json

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

        file = GDrive.download_file(game_config_file_id)

        if file is None:
            message = "Configuration file ID is invalid, is missing or you don't have access."

            logger.error(message)
            raise RuntimeError(message)

        file.seek(0)

        GameConfig.__games = json.load(file)
        GameConfig.__games_mapping = {game["name"]: game for game in GameConfig.__games}

        logger.info("Configuration for following games was found = %s", ", ".join(GameConfig.__games_mapping.keys()))

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
    def game_prop(property_name: str):
        """
        Used to get property from configuration of game that is in state.
        """

        selected_game = AppState.get_game()

        if selected_game not in GameConfig.__games_mapping:
            selected_game = GameConfig.game_names()[0]
            AppState.set_game(selected_game)

        return GameConfig.__games_mapping[selected_game][property_name]
