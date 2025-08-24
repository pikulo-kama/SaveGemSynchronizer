import os

from constants import JSON_EXTENSION
from src.core.AppState import AppState
from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_config, LOCALE_DIR

main_config = JsonConfigHolder(resolve_config('main.json'))
games_map = {game["name"]: game for game in JsonConfigHolder(resolve_config('games.json')).get()}
locales = [file.replace(JSON_EXTENSION, "") for file in os.listdir(LOCALE_DIR)]


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/main.json)
    """
    return main_config.get_value(property_name)


def games():
    return games_map.values()


def game(game_name: str):
    return games_map[game_name]


def game_prop(property_name: str):
    return game(AppState.get_game())[property_name]
