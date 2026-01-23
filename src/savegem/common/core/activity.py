import json

from kui.core.shortcut import dynamic_data
from kutil.logger import get_logger

from src.savegem.constants import HolderObject
from src.savegem.common.core.app_data import AppData
from src.savegem.common.service.gdrive import GDrive


_logger = get_logger(__name__)


class Activity(AppData):
    """
    Contains list of active players for current game
    """

    def __init__(self, context):
        super().__init__(context)
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
        activity_log = dynamic_data(HolderObject.Activity)
        _logger.debug("Activity log: %s", activity_log)

        for user_email, games in activity_log.items():
            if self.app.games.current.name in games:
                self.__players.append(self.app.users.by_email(user_email))
