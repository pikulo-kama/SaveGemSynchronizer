import json

from savegem.common.core import app
from savegem.common.service.gdrive import GDrive
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class PlayerService:
    """
    Used for interaction with player activity log
    file which is stored on Google Drive.
    """

    __NAME_PROP = "name"
    __GAMES_PROP = "games"

    @classmethod
    def get_active_players(cls, game_name: str):
        """
        Used to get list of players currently
        playing provided game.
        """

        players = []

        with GDrive.download_file(app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            for machine_id, activity in activity_log.items():

                # Do not display current user.
                # Only list other players that are online.
                if machine_id == app.user.machine_id:
                    continue

                if game_name in activity.get(cls.__GAMES_PROP):
                    players.append(activity.get(cls.__NAME_PROP, ""))

        return players

    @classmethod
    def update_activity_data(cls, game_names: list[str]):
        """
        Used to update activity log file on Google Drive.
        Will set provided languages for currently authenticated user.

        Will additionally delete all old records from activity data.
        """

        with GDrive.download_file(app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            _logger.debug("Log Before: %s", activity_log)

            if len(game_names) > 0:
                activity_log[app.user.machine_id] = {
                    cls.__NAME_PROP: app.user.name,
                    cls.__GAMES_PROP: game_names
                }

            # If there are no games running then remove
            # user entry from activity log.
            elif app.user.machine_id in activity_log:
                del activity_log[app.user.machine_id]

            _logger.debug("Log After: %s", activity_log)
            GDrive.update_file(app.config.activity_log_file_id, json.dumps(activity_log, indent=2))
