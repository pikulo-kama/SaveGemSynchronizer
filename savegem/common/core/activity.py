import json

from savegem.app.data import holder
from savegem.common.core.app_data import AppData
from savegem.common.service.gdrive import GDrive
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class Activity(AppData):
    """
    Contains list of active players for current game
    """

    NAME_PROP = "name"
    GAMES_PROP = "games"

    def __init__(self, app):
        super().__init__(app)
        self.__players = []

    @property
    def players(self):
        """
        Used to get list of active players.
        """
        return list(self.__players)

    def update(self, game_names):
        """
        Used to update activity of current user.
        """

        with GDrive.download_file(self.app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            _logger.debug("Log Before: %s", activity_log)

            if len(game_names) > 0:
                activity_log[self.app.users.current.email] = game_names

            # If there are no games running then remove
            # user entry from activity log.
            elif self.app.users.current.email in activity_log:
                del activity_log[self.app.users.current.email]

            _logger.debug("Log After: %s", activity_log)
            GDrive.update_file(self.app.config.activity_log_file_id, json.dumps(activity_log, indent=2))

    def refresh(self):
        """
        Used to download activity data from drive.
        """

        self.__players.clear()
        activity_log = holder().get("activity")

        for user_email, games in activity_log.items():
            if self.app.games.current.name in games:
                self.__players.append(self.app.users.by_email(user_email))
