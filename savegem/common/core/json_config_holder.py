from constants import JSON_EXTENSION
from savegem.common.util.file import read_file


class JsonConfigHolder:
    """
    Wrapper to work with JSON configuration.
    Only allows read operations.
    """

    def __init__(self, config_path: str):

        if not config_path.endswith(JSON_EXTENSION):
            config_path += JSON_EXTENSION

        self._config_path = config_path
        self._data = dict()

        self._before_file_open()

        self._load_data()

    def get_value(self, property_name, default_value=None):
        """
        Used to get property value from configuration.
        """

        if property_name not in self._data:
            return default_value

        return self._data.get(property_name)

    def get(self):
        """
        Used to get full configuration as map.
        """
        return self._data

    def _load_data(self):
        """
        Used to read configuration file
        and store contents in holder.

        Needed for testing purposes.
        """
        self._data = read_file(self._config_path, as_json=True)

    def _before_file_open(self):
        """
        To be overridden in child classes.
        Allows to perform additional operation before file opening began.
        """
        pass
