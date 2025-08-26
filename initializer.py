import os

from constants import APP_DATA_ROOT
from src.core.game_config import GameConfig
from src.util.file import OUTPUT_DIR, LOGS_DIR
from src.util.logger import initialize_logging


def init():
    """
    Used to initialize application mandatory resources.
    """

    for directory in [APP_DATA_ROOT, OUTPUT_DIR, LOGS_DIR]:
        # Create all required directories.
        if not os.path.exists(directory):
            os.makedirs(directory)

    initialize_logging()
    GameConfig.download()


init()
