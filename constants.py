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
    Styles: Final = os.path.join(ProjectRoot, "styles")

    # We need to have fallback value for APPDATA token, since
    # when tests are executed on Linux environment it would fail.
    AppDataRoot = os.path.join(os.getenv("APPDATA") or "", "SaveGem")
    Output: Final = os.path.join(AppDataRoot, "Output")
    Logs: Final = os.path.join(AppDataRoot, "Logs")
    Logback: Final = os.path.join(AppDataRoot, "Logback")


class File:
    """
    Contains names of files that are created/used by application.
    """

    GDriveToken: Final = "token.json"
    GDriveCreds: Final = "credentials.json"
    GDriveConfig: Final = "config.json"

    AppConfig: Final = "app.json"
    AppState: Final = "state.json"
    Style: Final = "style.json"

    GUIInitializedFlag: Final = "gui_init.flag"


class Resource:
    """
    Contains name of resource files
    """

    ApplicationIco: Final = "application.ico"
    NotificationIco: Final = "notification.ico"
    ConfirmationIco: Final = "confirmation.ico"


JSON_EXTENSION: Final = ".json"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"
JSON_MIME_TYPE: Final = "application/json"

UTF_8: Final = "utf-8"
SHA_256: Final = "sha256"
