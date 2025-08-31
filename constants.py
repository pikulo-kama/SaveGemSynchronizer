import os
from typing import Final


class Directory:
    """
    Contains names of directories used by application.
    """

    ProjectRoot: Final = os.path.dirname(os.path.abspath(__file__))
    Config: Final = os.path.join(ProjectRoot, "config")
    Locale: Final = os.path.join(ProjectRoot, "locale")
    Resources: Final = os.path.join(ProjectRoot, "resources")

    AppDataRoot = os.path.join(os.getenv("APPDATA"), "SaveGem")
    Output: Final = os.path.join(AppDataRoot, "output")
    Logs: Final = os.path.join(AppDataRoot, "logs")


JSON_EXTENSION: Final = ".json"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"
