from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.holders import prop
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class PropResolver(ContentResolver):
    """
    A specialized ContentResolver that retrieves values from the application's
    configuration properties.

    This resolver allows UI components to dynamically bind to static or
    environment-based configurations (e.g., API endpoints, version numbers,
    or global flags) using tokens like 'prop{app.version}'.
    """

    def resolve(self, property_name: str, *args, **kw):
        """
        Fetches the requested property from the global property holder.

        Args:
            property_name (str): The name of the configuration property to resolve.
            *args: Unused positional arguments.
            **kw: Unused keyword arguments.

        Returns:
            Any: The value of the property as defined in the application
                 configuration.
        """

        property_value = prop(property_name)

        _logger.debug("Resolving property %s to %s", property_name, property_value)
        return property_value
