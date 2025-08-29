import os

# Frequently accessed directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA_ROOT = os.path.join(os.getenv("APPDATA"), "SaveGem")

JSON_EXTENSION = ".json"
ZIP_EXTENSION = "zip"
ZIP_MIME_TYPE = "application/zip"

# Global state properties
STATE_SELECTED_GAME = "game"
STATE_SELECTED_LOCALE = "locale"

# File constants
LOG_FILE_NAME = "application.log"
LOGBACK_FILE_NAME = "logback.json"
GDRIVE_TOKEN_FILE_NAME = "token.json"
CREDENTIALS_FILE_NAME = "credentials.json"
GAME_CONFIG_POINTER_FILE_NAME = "game-config-file-id.txt"
