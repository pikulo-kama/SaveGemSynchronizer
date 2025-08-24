import os

# Frequently accessed directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA_ROOT = os.path.join(os.getenv("APPDATA"), "SaveGem")

JSON_EXTENSION = ".json"
ZIP_EXTENSION = "zip"
ZIP_MIME_TYPE = "application/zip"
CSV_MIME_TYPE = "text/csv"

# Active user GUI section constants
ACTIVE_USER_STATE_LABEL = "⚫"

# Application events
EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL = "upload.download.successful"
EVENT_GAME_SELECTION_CHANGED = "game.selection.changed"

# Global state properties
STATE_SELECTED_GAME = "game"
STATE_SELECTED_LOCALE = "locale"

# Local file system constants
GCLOUD_TOKEN_FILE_NAME = "gcloud_token.json"
CREDENTIALS_FILE_NAME = "credentials.json"
SAVE_VERSION_FILE_NAME = "save_version.json"
XBOX_CACHED_ACCESS_MAP = "xbox_access_map.json"

VALHEIM_XBOX_ACCESS_MAP_FILE_ID = "1FtTbXHsrhIzQ51FbSOP5yyk3P34yegBIEqVfhKgCloY"

# Xbox Live constants
XBOX_TOKEN_FILE_NAME = "xbox_tokens.json"
XBOX_SECRET_FILE_NAME = "xbox_secret.txt"

XBOX_VALHEIM_PRESENCE = "Valheim"
XBOX_ONLINE_STATE = "Online"
