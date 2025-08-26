import os

from constants import JSON_EXTENSION
from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_config, LOCALE_DIR
from src.util.logger import get_logger

logger = get_logger(__name__)

main_config = JsonConfigHolder(resolve_config("main.json"))
locales = [file.replace(JSON_EXTENSION, "") for file in os.listdir(LOCALE_DIR)]

logger.debug("Main config - %s", main_config)
logger.debug("Locale list - %s", locales)


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/main.json)
    """
    return main_config.get_value(property_name)
