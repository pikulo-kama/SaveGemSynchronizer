import os.path

from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import save_file


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
        save_file(self._config_path, self._data, as_json=True)

    def set(self, value: any):
        """
        Used to set configuration.
        This will fully replace existing configuration.
        """
        self._data = value
        save_file(self._config_path, self._data, as_json=True)

    def _before_file_open(self):
        if not os.path.exists(self._config_path):
            save_file(self._config_path, {}, as_json=True)
