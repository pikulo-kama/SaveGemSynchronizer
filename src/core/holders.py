import os

from constants import Directory, File
from src.core.json_config_holder import JsonConfigHolder
from src.util.file import resolve_config, remove_extension_from_path

_main_config = JsonConfigHolder(resolve_config(File.GUIConfig))
locales = [remove_extension_from_path(file) for file in os.listdir(Directory.Locale)]


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/gui.json)
    """

    parts = property_name.split(".")
    value = _main_config.get_value(parts.pop(0))

    for property_part in parts:
        value = value[property_part]

    return value
