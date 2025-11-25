from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.text_resource import tr
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class TrResolver(ContentResolver):
    """
    Used to resolve text resource messages.
    """

    def resolve(self, text_resource: str, *args, **kw):
        value = tr(text_resource, *args)

        _logger.debug("Resolving text resource %s with args %s", text_resource, args)
        _logger.debug("value=%s", value)
        return value
