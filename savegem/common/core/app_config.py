from typing import Final

from kui.core.app import KamaApplication
from kui.core.json_holder import JsonConfigHolder
from kutil.logger import get_logger

from savegem.constants import File
from savegem.common.core.app_data import AppData


_logger = get_logger(__name__)


class AppConfig(AppData):
    """
    Represents internal configuration
    which is part of the built exe and available only on runtime.
    """

    ActivityLogFileProp: Final = "activityLogFileId"
    GameConfigFileProp: Final = "gameConfigFileId"
    UsersConfigFileProp: Final = "usersConfigFileId"

    def __init__(self, context):
        super().__init__(context)

        application = KamaApplication()
        self.__config = JsonConfigHolder(application.discovery.get_project_root(File.GDriveConfig))

        _logger.debug("Activity Log File ID - %s", self.activity_log_file_id)
        _logger.debug("Game Config File ID - %s", self.games_config_file_id)
        _logger.debug("Users Config File ID - %s", self.users_config_file_id)

    @property
    def games_config_file_id(self):
        """
        ID of file in Google Drive that
        contains games configuration.
        """
        return self.__config.get_value(AppConfig.GameConfigFileProp)

    @property
    def activity_log_file_id(self):
        """
        ID of file in Google Drive that
        contains information about which games are currently
        being played by other players.
        """
        return self.__config.get_value(AppConfig.ActivityLogFileProp)

    @property
    def users_config_file_id(self):
        """
        ID of file in Google Drive that
        contains information about application
        users.
        """
        return self.__config.get_value(AppConfig.UsersConfigFileProp)

    def refresh(self):  # pragma: no cover
        # No need to reload config since it
        # is not modified by application.
        pass
