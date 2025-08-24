
import json
import os.path

from src.core.JsonConfigHolder import JsonConfigHolder


class EditableJsonConfigHolder(JsonConfigHolder):

    def set_value(self, property_name: str, value: any):
        self._data[property_name] = value

    def save(self):
        self.__save_internal(self._data)

    def _before_file_open(self):
        if not os.path.exists(self._config_path):
            self.__save_internal({})

    def __save_internal(self, data):
        with open(self._config_path, "w", encoding='utf-8') as f:
            json.dump(data, f)
