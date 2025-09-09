import json
from datetime import datetime

from src.core import app
from src.service.gdrive import GDrive
from src.util.logger import get_logger

_logger = get_logger(__name__)


class PlayerService:
    """
    Used for interaction with player activity log
    file which is stored on Google Drive.
    """

    __TIMESTAMP_PROP = "timestamp"
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

            for user_email, activity in activity_log.items():
                if game_name in activity.get(cls.__GAMES_PROP):
                    players.append(user_email)

        return players

    @classmethod
    def update_activity_data(cls, game_names: list[str], cleanup_interval: int = 60):
        """
        Used to update activity log file on Google Drive.
        Will set provided languages for currently authenticated user.

        Will additionally delete all old records from activity data.
        """

        with GDrive.download_file(app.config.activity_log_file_id) as log_bytes:
            log_bytes.seek(0)
            activity_log: dict = json.load(log_bytes)

            _logger.debug("Log Before: %s", activity_log)
            cls.__cleanup_log(activity_log, cleanup_interval)

            activity_log[app.user.name] = {
                cls.__TIMESTAMP_PROP: datetime.now().isoformat(),
                cls.__GAMES_PROP: game_names
            }

            _logger.debug("Log After: %s", activity_log)
            GDrive.update_file(app.config.activity_log_file_id, json.dumps(activity_log))

    @classmethod
    def __cleanup_log(cls, log_file: dict, cleanup_interval: int):
        """
        Used to remove old records from activity log.
        """

        now = datetime.now()

        for user_email in list(log_file.keys()):

            data = log_file.get(user_email)
            timestamp = datetime.fromisoformat(data.get(cls.__TIMESTAMP_PROP))
            elapsed_seconds = (now - timestamp).total_seconds()

            _logger.debug("user=%s, elapsed_time=%d", user_email, elapsed_seconds)

            if elapsed_seconds >= cleanup_interval:
                del log_file[user_email]
