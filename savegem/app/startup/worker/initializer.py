from savegem.app.startup import QStartupWorker
from savegem.common.core.context import app


class InitializationWorker(QStartupWorker):
    """
    Used to initialize all application state.
    """

    def _run(self):
        app().users.initialize()
        app().state.refresh()
        app().games.initialize()

        for game in app().games:
            game.meta.local.calculate_checksum()
            game.meta.drive.refresh()

        app().activity.refresh()

    @property
    def dependencies(self) -> list[str]:
        return [
            "ActivityWorker",
            "GameConfigDownloadWorker",
            "CurrentUserDownloadWorker",
            "AllUsersDownloadWorker",
            "UserDataDownloadWorker"
        ]
