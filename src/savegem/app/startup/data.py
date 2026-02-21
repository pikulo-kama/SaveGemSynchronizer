from kui.core.shortcut import add_dynamic_data
from kui.core.service.startup import KamaStartupWorker
from kutil.logger import get_logger

from savegem.constants import HolderObject
from savegem.common.core.context import context
from savegem.common.service.gdrive import GDrive


_logger = get_logger(__name__)


def download_file(key: str, file_id: str):
    add_dynamic_data(key, GDrive.download_json_file(file_id))


class CurrentUserDownloadWorker(KamaStartupWorker):
    """
    Used to download authenticated user data.
    """

    def _run(self):
        add_dynamic_data(HolderObject.CurrentUser, GDrive.get_current_user())


class AllUsersDownloadWorker(KamaStartupWorker):
    """
    Used to download data of all users that have access to the application.
    """

    def _run(self):
        add_dynamic_data(HolderObject.AllUsers, GDrive.get_users_with_access(context().config.games_config_file_id))


class UserDataDownloadWorker(KamaStartupWorker):
    """
    Used to download configuration file containing additional user data.
    """

    def _run(self):
        download_file(HolderObject.UserData, context().config.users_config_file_id)


class ActivityWorker(KamaStartupWorker):
    """
    Used to download activity data from drive.
    """

    def _run(self):
        download_file(HolderObject.Activity, context().config.activity_log_file_id)


class GameConfigDownloadWorker(KamaStartupWorker):
    """
    Used to download games' configuration from drive.
    """

    def _run(self):
        download_file(HolderObject.GamesConfig, context().config.games_config_file_id)


class AppSettingsDownloadWorker(KamaStartupWorker):
    """
    Used to download app settings from drive.
    """

    def _run(self):
        download_file(HolderObject.AppSettings, context().config.app_settings_file_id)
