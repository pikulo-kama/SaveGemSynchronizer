from kui.core.app import KamaApplication
from kui.core.service.startup import KamaStartupWorker
from savegem.common.core.context import context


class InitializationWorker(KamaStartupWorker):
    """
    Used to initialize all application state.
    """

    def _run(self):
        application = KamaApplication()
        version = application.config.version

        context().users.initialize()
        context().state.refresh()
        context().settings.initialize()

        if context().state.locale is None:
            context().state.locale = application.config.default_locale

        application.translations.locale = context().state.locale
        application.style.color_mode = context().state.color_theme

        # Don't load games and activity from drive
        # if version is outdated to avoid breaking
        # application.
        if context().settings.is_version_valid(version):
            context().games.initialize()

            for game in context().games:
                game.meta.local.calculate_checksum()
                game.meta.drive.refresh()

            context().activity.refresh()

    @property
    def dependencies(self) -> list[str]:
        return [
            "ActivityWorker",
            "GameConfigDownloadWorker",
            "CurrentUserDownloadWorker",
            "AllUsersDownloadWorker",
            "UserDataDownloadWorker"
        ]
