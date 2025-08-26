
import json
import os.path

from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import save_file


class EditableJsonConfigHolder(JsonConfigHolder):
    """
    Used to operate with JSON configurations.
    Allows both read and write operations.
    """

    def set_value(self, property_name: str, value: any):
        """
        Used to set json property in configuration.
        """
        self._data[property_name] = value
        self.__save(self._data)

    def set(self, value: any):
        """
        Used to set configuration.
        This will fully replace existing configuration.
        """
        self._data = value
        self.__save(self._data)

    def _before_file_open(self):
        if not os.path.exists(self._config_path):
            self.__save({})

    def __save(self, data: any):
        """
        Used to save configuration with all its changes to the file system.
        """

        # Can't use property from config since it wil result in circular dependency.
        save_file(self._config_path, data, as_json=True)
