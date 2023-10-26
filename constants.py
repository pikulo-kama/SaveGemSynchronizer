import os
from datetime import date

# General use constants
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_EXTENSION = "zip"
ZIP_MIME_TYPE = "application/zip"

APPLICATION_ICO = "valheim_synchronizer.ico"

# Main window constants
WINDOW_TITLE = "Синхронізатор для Valheim"
WINDOW_DEFAULT_WIDTH = 1080
WINDOW_DEFAULT_HEIGHT = 720
UPLOAD_LABEL = "Відвантажити"
DOWNLOAD_LABEL = "Завантажити"
COPYRIGHT_LABEL = f"© 2023{'' if date.today().year == 2023 else f'-{date.today().year}'} Артур Паркур. Всі права захищені."

# Notification window constants
NOTIFICATION_WINDOW_TITLE = "Інформасьйон"
NOTIFICATION_WINDOW_WIDTH = 400
NOTIFICATION_WINDOW_HEIGHT = 150
NOTIFICATION_WINDOW_CLOSE_BTN = "OK"

# Confirmation window constants
CONFIRMATION_WINDOW_TITLE = "Застереження"
CONFIRMATION_WINDOW_WIDTH = NOTIFICATION_WINDOW_WIDTH
CONFIRMATION_WINDOW_HEIGHT = NOTIFICATION_WINDOW_HEIGHT
CONFIRMATION_WINDOW_CLOSE_BTN = "Передумав"
CONFIRMATION_WINDOW_CONFIRM_BTN = "Підтверджую"

# Notification messages
NOTIFICATION_UPLOAD_COMPLETED_MSG = "Сейв успішно відвантажено."
NOTIFICATION_NO_SAVES_PRESENT_MSG = "Cховище порожнє. Потрібно виконати відвантаження."
NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG = "Свіженький сейв успішно завантажено."

# Confirmation messages
CONFIRMATION_BEFORE_DOWNLOAD_MSG = "Впевнений? Це знищить твій існуючий сейв."

# Google Drive constants / Local file system constants
TOKEN_FILE_NAME = "token.json"
SECRET_FILE_NAME = "credentials.json"

VALHEIM_LOCAL_SAVES_DIR = os.path.expandvars("%localappdata%low\\IronGate\\Valheim\\worlds_local")
VALHEIM_SAVES_DIR_ID = "11KNPgZ_pEXm1Ur0uqZMggaJidezOZCZU"
