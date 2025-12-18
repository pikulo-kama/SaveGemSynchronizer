from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.text_resource import tr
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class TrResolver(ContentResolver):
    """
    A specialized ContentResolver for internationalization and localization.

    This resolver uses the 'tr' utility to look up translated strings in the
    application's text resources, supporting dynamic argument replacement
    for parameterized messages.
    """

    def resolve(self, text_resource: str, *args, **kw):
        """
        Translates a resource key into its localized string value.

        Args:
            text_resource (str): The key/identifier for the text resource.
            *args: Positional arguments used for string formatting within the
                   translated message.
            **kw: Unused keyword arguments.

        Returns:
            str: The localized and formatted string.
        """

        value = tr(text_resource, *args)

        _logger.debug("Resolving text resource %s with args %s", text_resource, args)
        _logger.debug("value=%s", value)

        return value
