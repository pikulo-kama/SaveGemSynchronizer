from src.core.app_state import AppState
from src.core.json_config_holder import JsonConfigHolder
from src.core.holders import prop
from src.util.file import resolve_locale
from src.util.logger import get_logger

logger = get_logger(__name__)


def tr(key: str, *args) -> str:
    """
    Used to resolve text resource based on the currently selected language.
    """
    locale = AppState.get_locale(prop("defaultLocale"))
    return TextResource.get(locale, key, *args)


class TextResource:
    """
    Used to resolve text resources.
    """

    current_locale = None
    holder = None

    @staticmethod
    def get(locale: str, key: str, *args) -> str:
        """
        Gets text resource by key using currently selected game.
        If text resources has placeholder and arguments have been provided then they would be resolved.
        """

        if TextResource.current_locale != locale:
            logger.info("Locale selection has been changed. Initializing holder for %s", locale)
            TextResource.current_locale = locale
            TextResource.holder = JsonConfigHolder(resolve_locale(locale))

        label = str(TextResource.holder.get_value(key))
        logger.debug("TextResource '%s.%s' = %s", locale, key, label)

        if len(args) > 0:
            logger.debug("TextResource Args = %s", args)
            label = label.format(*args)

        return label
