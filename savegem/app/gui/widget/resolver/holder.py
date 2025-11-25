from savegem.app.data import holder
from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class DataResolver(ContentResolver):
    """
    Used to resolve value from data holder
    global object.

    Will only return value if value is of
    string type.
    """

    def resolve(self, key: str, *args, **kw):

        data = holder().get(key)

        if isinstance(data, str):
            _logger.debug("Resolved %s to %s", key, data)
            return data

        return ""
