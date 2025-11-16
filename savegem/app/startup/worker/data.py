from savegem.app.data import holder, HolderObject
from savegem.app.startup.worker import QStartupWorker
from savegem.common.core.context import app
from savegem.common.service.gdrive import GDrive


class CurrentUserDownloadWorker(QStartupWorker):
    """
    Used to download authenticated user data.
    """

    def _run(self):
        holder().add(HolderObject.CurrentUser, GDrive.get_current_user())


class AllUsersDownloadWorker(QStartupWorker):
    """
    Used to download data of all users that have access to the application.
    """

    def _run(self):
        holder().add(HolderObject.AllUsers, GDrive.get_users_with_access(app().config.games_config_file_id))


class UserDataDownloadWorker(QStartupWorker):
    """
    Used to download configuration file containing additional user data.
    """

    def _run(self):
        holder().download_json(HolderObject.UserData, app().config.users_config_file_id)


class ActivityWorker(QStartupWorker):
    """
    Used to download activity data from drive.
    """

    def _run(self):
        holder().download_json(HolderObject.Activity, app().config.activity_log_file_id)


class GameConfigDownloadWorker(QStartupWorker):
    """
    Used to download games' configuration from drive.
    """

    def _run(self):
        holder().download_json(HolderObject.GamesConfig, app().config.games_config_file_id)
