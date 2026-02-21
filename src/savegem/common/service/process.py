from abc import ABC

from kui.core.app import KamaApplication
from kui.core.shortcut import add_dynamic_data, dynamic_data

from savegem.common.core.context import context
from savegem.common.service.daemon import Daemon
from savegem.common.service.gdrive import GDrive
from savegem.constants import HolderObject


def validate_version(func):

    def wrapper(self, *args, **kwargs):
        application = KamaApplication()
        version = application.config.version

        if not context().settings.is_version_valid(version):
            return None

        return func(self, *args, **kwargs)

    return wrapper


class AppDaemon(Daemon, ABC):

    def _run_once(self):
        application = KamaApplication()
        version = application.config.version

        add_dynamic_data(HolderObject.CurrentUser, GDrive.get_current_user())
        # No need to get all users that have access since GDrive watcher
        # only needs current user information.
        add_dynamic_data(HolderObject.AllUsers, [dynamic_data(HolderObject.CurrentUser)])
        add_dynamic_data(HolderObject.UserData, GDrive.download_json_file(context().config.users_config_file_id))
        add_dynamic_data(HolderObject.GamesConfig, GDrive.download_json_file(context().config.games_config_file_id))
        add_dynamic_data(HolderObject.AppSettings, GDrive.download_json_file(context().config.app_settings_file_id))

        context().users.initialize()
        context().settings.initialize()
        context().state.refresh()

        application.translations.locale = context().state.locale

        if context().settings.is_version_valid(version):
            context().games.initialize()
