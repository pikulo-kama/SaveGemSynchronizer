from savegem.common.core.context import app
from savegem.common.db.manager import db
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


def tr(key: str, *args) -> str:
    """
    Used to resolve text resource based on the currently selected language.
    """
    return TextResource.get(app().state.locale, key, *args)


class TextResource:
    """
    Used to resolve text resources.
    """

    __current_locale = None
    __resource_map = {}

    @classmethod
    def get(cls, locale: str, key: str, *args) -> str:
        """
        Gets text resource by key using currently selected game.
        If text resources has placeholder and arguments have been provided then they would be resolved.
        """

        if cls.__current_locale != locale:
            _logger.info("Locale selection has been changed. Initializing holder for %s", locale)
            cls.__current_locale = locale
            cls.__initialize_text_resources(locale)

        label = cls.__resource_map.get(key, key)
        _logger.debug("TextResource '%s.%s' = %s", locale, key, label)

        if len(args) > 0:
            _logger.debug("TextResource Args = %s", args)
            label = label.format(*args)

        return label

    @classmethod
    def reset(cls):
        """
        Used to reset loaded translations.
        """

        cls.__current_locale = None
        cls.__resource_map = {}

    @classmethod
    def __initialize_text_resources(cls, locale_id: str):
        """
        Used to load text resources
        that correspond provided locale ID.
        """

        resources = db().table("setup_text_resource") \
            .where("locale_id = ?", locale_id) \
            .retrieve()

        for resource in resources:
            key = resource.get("text_resource_key")
            value = resource.get("text_resource")

            cls.__resource_map[key] = value
