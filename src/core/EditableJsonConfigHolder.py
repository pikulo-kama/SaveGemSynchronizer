
import json
import os.path

from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.logger import get_logger

logger = get_logger(__name__)


class EditableJsonConfigHolder(JsonConfigHolder):

    def set_value(self, property_name: str, value: any):
        self._data[property_name] = value
        self.save()

    def save(self):
        self.__save_internal(self._data)

    def _before_file_open(self):
        if not os.path.exists(self._config_path):
            logger.info("File %s is missing and would be created.", self._config_path)
            self.__save_internal({})

    def __save_internal(self, data):
        with open(self._config_path, "w", encoding='utf-8') as f:
            logger.debug("Saving data to %s - %s", self._config_path, data)
            json.dump(data, f)
