from savegem.common.core import app
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import resolve_locale
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


def tr(key: str, *args) -> str:
    """
    Used to resolve text resource based on the currently selected language.
    """
    return TextResource.get(app.state.locale, key, *args)


class TextResource:
    """
    Used to resolve text resources.
    """

    __current_locale = None
    __holder = None

    @classmethod
    def get(cls, locale: str, key: str, *args) -> str:
        """
        Gets text resource by key using currently selected game.
        If text resources has placeholder and arguments have been provided then they would be resolved.
        """

        if cls.__current_locale != locale:
            _logger.info("Locale selection has been changed. Initializing holder for %s", locale)
            cls.__current_locale = locale
            cls.__holder = JsonConfigHolder(resolve_locale(locale))

        label = str(cls.__holder.get_value(key))
        _logger.debug("TextResource '%s.%s' = %s", locale, key, label)

        if len(args) > 0:
            _logger.debug("TextResource Args = %s", args)
            label = label.format(*args)

        return label
