
import json

from constants import JSON_EXTENSION


class JsonConfigHolder:

    def __init__(self, config_path: str):

        if not config_path.endswith(JSON_EXTENSION):
            config_path += JSON_EXTENSION

        self._config_path = config_path
        self._data = dict()

        self._before_file_open()

        with open(self._config_path, encoding='utf-8') as f:
            self._data = json.load(f)

    def get_value(self, property_name):
        if property_name not in self._data:
            return None

        return self._data[property_name]

    def get(self):
        return self._data

    def _before_file_open(self):
        # To be overridden in child classes.
        pass
