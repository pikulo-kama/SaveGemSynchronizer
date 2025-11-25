from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.holders import prop
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class PropResolver(ContentResolver):
    """
    Used to resolve app configuration tokens.
    """

    def resolve(self, property_name: str, *args, **kw):
        property_value = prop(property_name)

        _logger.debug("Resolving property %s to %s", property_name, property_value)
        return property_value
