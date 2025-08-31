import os

from constants import APP_DATA_ROOT
from src.util.file import OUTPUT_DIR, LOGS_DIR


def init():
    """
    Used to initialize application mandatory resources.
    """

    for directory in [APP_DATA_ROOT, OUTPUT_DIR, LOGS_DIR]:
        # Create all required directories.
        if not os.path.exists(directory):
            os.makedirs(directory)

    from src.core import app
    from src.service.gdrive import GDrive
    from src.util.logger import initialize_logging

    initialize_logging()
    app.games.download()
    app.user.initialize(GDrive.get_current_user())


init()
