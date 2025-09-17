from constants import File
from savegem.common.core.app_data import AppData
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import resolve_project_data


class _AppConfig(AppData):
    """
    Represents internal configuration
    which is part of the built exe and available only on runtime.
    """

    def __init__(self):
        super().__init__()
        self.__config = JsonConfigHolder(resolve_project_data(File.GDriveConfig))

    @property
    def games_config_file_id(self):
        """
        ID of file in Google Drive that
        contains games configuration.
        """
        return self.__config.get_value("gameConfigFileId")

    @property
    def activity_log_file_id(self):
        """
        ID of file in Google Drive that
        contains information about which games are currently
        being played by other players.
        """
        return self.__config.get_value("activityLogFileId")

    def reload(self):
        # No need to reload config since it
        # is not modified by application.
        pass
