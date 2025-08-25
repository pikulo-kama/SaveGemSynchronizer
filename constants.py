import os

# Frequently accessed directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA_ROOT = os.path.join(os.getenv("APPDATA"), "SaveGem")

JSON_EXTENSION = ".json"
ZIP_EXTENSION = "zip"
ZIP_MIME_TYPE = "application/zip"
CSV_MIME_TYPE = "text/csv"

# Global state properties
STATE_SELECTED_GAME = "game"
STATE_SELECTED_LOCALE = "locale"

# File constants
LOG_FILE_NAME = "application.log"
LOGBACK_FILE_NAME = "logback.json"
GCLOUD_TOKEN_FILE_NAME = "gcloud_token.json"
CREDENTIALS_FILE_NAME = "credentials.json"
SAVE_VERSION_FILE_NAME = "save_version.json"
XBOX_ACCESS_MAP = "xbox_access_map.json"
XBOX_TOKEN_FILE_NAME = "xbox_token.json"
XBOX_SECRET_FILE_NAME = "xbox_secret.txt"

XBOX_ONLINE_STATE = "Online"
