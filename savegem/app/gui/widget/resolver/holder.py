from savegem.app.data import holder
from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class DataResolver(ContentResolver):
    """
    A specialized ContentResolver that retrieves dynamic values from the global
    data holder object.

    This resolver is typically used to inject application state data into UI
    components via tokens like 'data{user_name}'. It ensures type safety by
    only returning values that are explicitly of string type.
    """

    def resolve(self, key: str, *args, **kw):
        """
        Looks up the provided key in the global data holder and returns its
        string representation.

        Args:
            key (str): The identifier for the data to be retrieved.
            *args: Unused positional arguments.
            **kw: Unused keyword arguments.

        Returns:
            str: The resolved string value or an empty string if the data
                 is missing or not a string.
        """

        data = holder().get(key)

        if isinstance(data, str):
            _logger.debug("Resolved %s to %s", key, data)
            return data

        return None
