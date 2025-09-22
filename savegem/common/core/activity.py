import json

from savegem.common.core.app_data import AppData
from savegem.common.service.gdrive import GDrive
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class _Activity(AppData):
    """
    Contains list of active players for current game
    """

    __NAME_PROP = "name"
    __GAMES_PROP = "games"

    def __init__(self):
        super().__init__()
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

        with GDrive.download_file(self._app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            _logger.debug("Log Before: %s", activity_log)

            if len(game_names) > 0:
                activity_log[self._app.user.machine_id] = {
                    self.__NAME_PROP: self._app.user.name,
                    self.__GAMES_PROP: game_names
                }

            # If there are no games running then remove
            # user entry from activity log.
            elif self._app.user.machine_id in activity_log:
                del activity_log[self._app.user.machine_id]

            _logger.debug("Log After: %s", activity_log)
            GDrive.update_file(self._app.config.activity_log_file_id, json.dumps(activity_log, indent=2))

    def reload(self):
        self.__players.clear()

        with GDrive.download_file(self._app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            for machine_id, activity in activity_log.items():

                # Do not display current user.
                # Only list other players that are online.
                if machine_id == self._app.user.machine_id:
                    continue

                if self._app.games.current.name in activity.get(self.__GAMES_PROP):
                    self.__players.append(activity.get(self.__NAME_PROP, ""))
