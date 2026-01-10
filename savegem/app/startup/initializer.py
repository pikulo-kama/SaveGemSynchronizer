from kui.core.service.startup import KamaStartupWorker
from savegem.common.core.context import context


class InitializationWorker(KamaStartupWorker):
    """
    Used to initialize all application state.
    """

    def _run(self):
        context().users.initialize()
        context().state.refresh()
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
