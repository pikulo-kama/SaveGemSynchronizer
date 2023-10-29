import os
from datetime import date

# General use constants
APPLICATION_VERSION = "2.0.0"
APPLICATION_LOCALE = "uk_UA"
TZ_PLUS_HOURS = 3

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_EXTENSION = "zip"
ZIP_MIME_TYPE = "application/zip"
CSV_MIME_TYPE = "text/csv"

APPLICATION_ICO = "valheim_synchronizer.ico"

# Main window constants
WINDOW_TITLE = "Синхронізатор для Valheim"
WINDOW_DEFAULT_WIDTH = 1080
WINDOW_DEFAULT_HEIGHT = 720
UPLOAD_LABEL = "🠉 Відвантажити"
DOWNLOAD_LABEL = "🠋"
APPLICATION_PRIMARY_TEXT_COLOR = "#009688"
APPLICATION_SECONDARY_TEXT_COLOR = "#068076"

SAVE_UP_TO_DATE_LABEL = "Нічого нового... Твій сейв свіженький як ніколи."
SAVE_OUTDATED_LABEL = "Здалося б оновитись.."
LAST_SAVE_INFO_LABEL = "Останній сейв {0} o {1} від {2}"

# Active user GUI section constants
ACTIVE_USER_STATE_LABEL = "⚫"

ACTIVE_USER_IS_PLAYING_COLOR = "#32CD32"
ACTIVE_USER_NOT_PLAYING_COLOR = "#d95b25"
ACTIVE_USER_TEXT_COLOR = "#a4a8ab"

# Application events
EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL = "upload.download.successful"

# Button colors
UPLOAD_BTN_PROPERTIES = {
    "colorStatic": "#ddedde",
    "colorHover": "#dae6db",
    "width": 35
}

DOWNLOAD_BTN_PROPERTIES = {
    "colorStatic": "#cedfeb",
    "colorHover": "#d5dde3",
    "width": 5
}

BTN_PROPERTY_LIST = [UPLOAD_BTN_PROPERTIES, DOWNLOAD_BTN_PROPERTIES]

COPYRIGHT_LABEL = f"© 2023{'' if date.today().year == 2023 else f'-{date.today().year}'} Артур Паркур. Всі права захищені."

# Notification window constants
NOTIFICATION_WINDOW_TITLE = "Інформасьйон"
NOTIFICATION_ICO = "notification.ico"
NOTIFICATION_WINDOW_WIDTH = 400
NOTIFICATION_WINDOW_HEIGHT = 150
NOTIFICATION_WINDOW_CLOSE_BTN = "OK"
NOTIFICATION_TEXT_COLOR = APPLICATION_SECONDARY_TEXT_COLOR

NOTIFICATION_CLOSE_BTN_PROPERTIES = UPLOAD_BTN_PROPERTIES

NOTIFICATION_POPUP_PROPERTY_LIST = [NOTIFICATION_CLOSE_BTN_PROPERTIES]

# Confirmation window constants
CONFIRMATION_WINDOW_TITLE = "Застереження"
CONFIRMATION_ICO = "confirmation.ico"
CONFIRMATION_WINDOW_WIDTH = NOTIFICATION_WINDOW_WIDTH
CONFIRMATION_WINDOW_HEIGHT = NOTIFICATION_WINDOW_HEIGHT
CONFIRMATION_WINDOW_CLOSE_BTN = "Передумав"
CONFIRMATION_WINDOW_CONFIRM_BTN = "Підтверджую"
CONFIRMATION_TEXT_COLOR = APPLICATION_SECONDARY_TEXT_COLOR


CONFIRMATION_CONFIRM_BTN_PROPERTIES = UPLOAD_BTN_PROPERTIES
CONFIRMATION_CANCEL_BTN_PROPERTIES = DOWNLOAD_BTN_PROPERTIES

CONFIRMATION_POPUP_PROPERTY_LIST = [CONFIRMATION_CONFIRM_BTN_PROPERTIES, CONFIRMATION_CANCEL_BTN_PROPERTIES]

# Notification messages
NOTIFICATION_UPLOAD_COMPLETED_MSG = "Сейв успішно відвантажено."
NOTIFICATION_NO_SAVES_PRESENT_MSG = "Cховище порожнє. Потрібно виконати відвантаження."
NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG = "Свіженький сейв успішно завантажено."

# Confirmation messages
CONFIRMATION_BEFORE_DOWNLOAD_MSG = "Впевнений? Це знищить твій існуючий сейв."

# Google Drive constants / Local file system constants
GCLOUD_TOKEN_FILE_NAME = "gcloud_token.json"
SECRET_FILE_NAME = "credentials.json"
SAVE_VERSION_FILE_NAME = "save_version.txt"
XBOX_ACCESS_MAP_DATE_UPDATE = "xbox_access_map_date_update.txt"
XBOX_CACHED_ACCESS_MAP = "xbox_access_map.cached.json"

VALHEIM_LOCAL_SAVES_DIR = os.path.expandvars("%localappdata%low\\IronGate\\Valheim\\worlds_local")
VALHEIM_SAVES_DIR_ID = "11KNPgZ_pEXm1Ur0uqZMggaJidezOZCZU"
VALHEIM_XBOX_ACCESS_MAP_FILE_ID = "1FtTbXHsrhIzQ51FbSOP5yyk3P34yegBIEqVfhKgCloY"

# Xbox Live constants
XBOX_CLIENT_ID = "7cc88370-21c2-43c6-bf9d-06f224740c0a"
XBOX_TOKEN_FILE_NAME = "xbox_tokens.json"
XBOX_SECRET_FILE_NAME = "xbox_secret.txt"

XBOX_VALHEIM_PRESENCE = "Valheim"
