from kui.core.app import KamaApplication
from kui.core.service.startup import KamaStartupWorker
from savegem.common.core.context import context


class InitializationWorker(KamaStartupWorker):
    """
    Used to initialize all application state.
    """

    def _run(self):
        application = KamaApplication()

        context().users.initialize()
        context().state.refresh()
        context().games.initialize()

        application.translations.locale = context().state.locale
        application.style.color_mode = context().state.color_theme

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
