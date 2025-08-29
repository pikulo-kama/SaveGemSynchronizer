import os
from typing import Final


PROJECT_ROOT: Final = os.path.dirname(os.path.abspath(__file__))
APP_DATA_ROOT: Final = os.path.join(os.getenv("APPDATA"), "SaveGem")

JSON_EXTENSION: Final = ".json"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"

# Global state properties
STATE_SELECTED_GAME: Final = "game"
STATE_SELECTED_LOCALE: Final = "locale"

# File constants
LOG_FILE_NAME: Final = "application.log"
LOGBACK_FILE_NAME: Final = "logback.json"
GDRIVE_TOKEN_FILE_NAME: Final = "token.json"
CREDENTIALS_FILE_NAME: Final = "credentials.json"
GAME_CONFIG_POINTER_FILE_NAME: Final = "game-config-file-id.txt"
