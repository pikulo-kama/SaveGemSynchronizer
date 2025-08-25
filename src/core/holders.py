import os

from constants import JSON_EXTENSION
from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_config, LOCALE_DIR
from src.util.logger import get_logger

logger = get_logger(__name__)

main_config = JsonConfigHolder(resolve_config("main.json"))
games_map = {game["name"]: game for game in JsonConfigHolder(resolve_config("games.json")).get()}
locales = [file.replace(JSON_EXTENSION, "") for file in os.listdir(LOCALE_DIR)]

logger.debug("Main config - %s", main_config)
logger.debug("Game name - configuration mapping - %s", games_map)
logger.debug("Locale list - %s", locales)


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/main.json)
    """
    return main_config.get_value(property_name)


def games():
    """
    Used to get list of game configurations.
    """
    return games_map.values()


def game_prop(property_name: str):
    """
    Used to get property from configuration of game that is in state.
    """
    from src.core.AppState import AppState
    return game(AppState.get_game())[property_name]


def game(game_name: str):
    """
    Used to get game configuration by name.
    """
    return games_map[game_name]
