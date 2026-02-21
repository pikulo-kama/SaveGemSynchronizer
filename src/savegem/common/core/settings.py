from kui.core.shortcut import dynamic_data

from savegem.common.core.app_data import AppData
from savegem.constants import HolderObject


class AppSettings(AppData):

    def __init__(self, context):
        super().__init__(context)
        self.__settings = {}

    def initialize(self):
        self.__settings = dynamic_data(HolderObject.AppSettings) or {}

    def is_version_valid(self, version: str):

        def replace_placeholders(first_arr: list[str], second_arr: list[str]):
            for idx, value in enumerate(first_arr):
                if value.lower() == "x":
                    first_arr[idx] = second_arr[idx]

            return first_arr

        def compare(first_version: str, second_version: str):
            first_version_arr: list[str] = first_version.split(".")
            second_version_arr: list[str] = second_version.split(".")

            first_version = "".join(replace_placeholders(first_version_arr, second_version_arr))
            second_version = "".join(replace_placeholders(second_version_arr, first_version_arr))

            return int(first_version) >= int(second_version)

        min_version = self.__settings.get("minVersion", version)
        max_version = self.__settings.get("maxVersion", version)

        return compare(version, min_version) and compare(max_version, version)

    def refresh(self):
        self.initialize()
