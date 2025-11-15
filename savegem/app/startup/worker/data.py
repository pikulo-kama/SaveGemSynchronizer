from savegem.app.data import holder
from savegem.app.startup.worker import QStartupWorker
from savegem.common.core.context import app
from savegem.common.service.gdrive import GDrive


class CurrentUserDownloadWorker(QStartupWorker):
    """
    Used to download authenticated user data.
    """

    def _run(self):
        holder().add("currentUser", GDrive.get_current_user())


class AllUsersDownloadWorker(QStartupWorker):
    """
    Used to download data of all users that have access to the application.
    """

    def _run(self):
        holder().add("allUsers", GDrive.get_users_with_access(app().config.games_config_file_id))


class UserConfigDownloadWorker(QStartupWorker):
    """
    Used to download configuration file containing additional user data.
    """

    def _run(self):
        holder().download_json("userData", app().config.users_config_file_id)


class ActivityWorker(QStartupWorker):
    """
    Used to download activity data from drive.
    """

    def _run(self):
        holder().download_json("activity", app().config.activity_log_file_id)


class GameConfigDownloadWorker(QStartupWorker):
    """
    Used to download games' configuration from drive.
    """

    def _run(self):
        holder().download_json("gamesConfig", app().config.games_config_file_id)
