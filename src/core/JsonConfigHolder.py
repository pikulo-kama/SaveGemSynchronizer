import json
from constants import JSON_EXTENSION


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

        # Can't use property from config since it wil result in circular dependency.
        with open(self._config_path, encoding="utf-8") as f:
            self._data = json.load(f)

    def get_value(self, property_name):
        """
        Used to get property value from configuration.
        """
        if property_name not in self._data:
            return None

        return self._data[property_name]

    def get(self):
        """
        Used to get full configuration as map.
        """
        return self._data

    def _before_file_open(self):
        """
        To be overridden in child classes.
        Allows to perform additional operation before file opening began.
        """
        pass
