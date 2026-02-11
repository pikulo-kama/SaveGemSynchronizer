from kui.core.resolver import ContentResolver
from savegem.common.core.context import context
from kutil.logger import get_logger


_logger = get_logger(__name__)


class UserResolver(ContentResolver):
    """
    Used to resolve user related properties.
    """

    def resolve(self, key: str, *args, **kw):
        value = ""

        if key == "name":
            value = context().users.current.name

        elif key == "photo":
            value = context().users.current.photo

        _logger.debug("Resolved '%s' to %s", key, value)
        return value
