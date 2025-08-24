import os

from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_config

main_config = JsonConfigHolder(resolve_config('main.json'))
games_map = {game["name"]: game for game in JsonConfigHolder(resolve_config('games.json')).get()}


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/main.json)
    """
    return main_config.get_value(property_name)


def games():
    return games_map.values()


def game(game_name: str):
    return games_map[game_name]
