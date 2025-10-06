from typing import Final

from constants import File
from savegem.common.core.app_data import AppData
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import resolve_project_data
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class AppConfig(AppData):
    """
    Represents internal configuration
    which is part of the built exe and available only on runtime.
    """

    ActivityLogFileProp: Final = "activityLogFileId"
    GameConfigFileProp: Final = "gameConfigFileId"

    def __init__(self):
        super().__init__()
        self.__config = JsonConfigHolder(resolve_project_data(File.GDriveConfig))

        _logger.debug("Activity Log File ID - %s", self.activity_log_file_id)
        _logger.debug("Game Config File ID - %s", self.games_config_file_id)

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

    def refresh(self):  # pragma: no cover
        # No need to reload config since it
        # is not modified by application.
        pass
