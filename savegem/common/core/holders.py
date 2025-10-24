from typing import Optional

from constants import File
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.db.manager import db
from savegem.common.util.file import resolve_config

_app_config: Optional[JsonConfigHolder] = None
_locales = None


def _get_app_config():
    global _app_config

    if _app_config is None:
        _app_config = JsonConfigHolder(resolve_config(File.AppConfig))

    return _app_config


def locales():
    """
    Used to get list of locale IDs configured in the system.
    """

    global _locales

    if _locales is None:
        locale_list = db().table("setup_locale").retrieve()
        _locales = [locale.get("locale_id") for locale in locale_list]

    return _locales


def prop(property_name: str):
    """
    Used to get property value from main configuration file (config/app.json)
    """

    parts = property_name.split(".")
    value = _get_app_config().get_value(parts.pop(0), {})

    for property_part in parts:
        value = value.get(property_part, {})

    return value
