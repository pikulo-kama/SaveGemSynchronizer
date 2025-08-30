import os

from constants import JSON_EXTENSION
from src.core.json_config_holder import JsonConfigHolder
from src.util.file import resolve_config, LOCALE_DIR
from src.util.logger import get_logger

_logger = get_logger(__name__)

_main_config = JsonConfigHolder(resolve_config("main"))
locales = [file.replace(JSON_EXTENSION, "") for file in os.listdir(LOCALE_DIR)]

_logger.debug("Main config - %s", _main_config)
_logger.debug("Locale list - %s", locales)


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/main.json)
    """

    parts = property_name.split(".")

    if len(parts) == 1:
        return _main_config.get_value(property_name)

    value = _main_config.get_value(parts.pop(0))

    for property_part in parts:
        value = value[property_part]

    return value
