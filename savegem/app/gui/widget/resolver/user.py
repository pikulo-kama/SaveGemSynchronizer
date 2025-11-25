from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class UserResolver(ContentResolver):
    """
    Used to resolve user related properties.
    """

    def resolve(self, key: str, *args, **kw):
        value = ""

        if key == "name":
            value = app().users.current.name

        elif key == "photo":
            value = app().users.current.photo

        _logger.debug("Resolved '%s' to %s", key, value)
        return value
