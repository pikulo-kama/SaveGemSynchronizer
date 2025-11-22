import json
from typing import Optional, Final
from savegem.common.service.gdrive import GDrive

_data_holder: Optional["DataHolder"] = None


class HolderObject:
    """
    Object names that are being stored
    in data holder.
    """

    CurrentUser: Final = "currentUser"
    AllUsers: Final = "allUsers"
    UserData: Final = "userData"

    Activity: Final = "activity"
    GamesConfig: Final = "gamesConfig"


class DataHolder:
    """
    Used as intermediate storage for data
    that has been downloaded by workers.
    """

    def __init__(self):
        self.__data = {}

    def download_json(self, object_name: str, file_id: str):
        """
        Used to download JSON file from drive
        and store it in holder.
        """

        with GDrive.download_file(file_id) as file_bytes:

            if file_bytes is None:
                self.add(object_name, None)
                return

            file_bytes.seek(0)
            self.add(object_name, json.load(file_bytes))

    def get(self, object_name: str):
        """
        Used to get data by name.
        """
        return self.__data.get(object_name)

    def add(self, object_name: str, data):
        """
        Used to add data to holder.
        """
        self.__data[object_name] = data


def holder():  # pragma: no cover
    """
    Used to get global data holder instance.
    """

    global _data_holder

    if _data_holder is None:
        _data_holder = DataHolder()

    return _data_holder
