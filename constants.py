import os
from typing import Final


PROJECT_ROOT: Final = os.path.dirname(os.path.abspath(__file__))
APP_DATA_ROOT: Final = os.path.join(os.getenv("APPDATA"), "SaveGem")

JSON_EXTENSION: Final = ".json"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"
