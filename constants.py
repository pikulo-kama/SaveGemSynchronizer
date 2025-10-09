import os
from typing import Final


class Directory:
    """
    Contains names of directories used by application.
    """

    @property
    def ProjectRoot(self):  # noqa
        return os.path.dirname(os.path.abspath(__file__))

    @property
    def Config(self):  # noqa
        return str(os.path.join(self.ProjectRoot, "config"))

    @property
    def Locale(self):  # noqa
        return os.path.join(self.ProjectRoot, "locale")

    @property
    def Resources(self):  # noqa
        return os.path.join(self.ProjectRoot, "resources")

    @property
    def Styles(self):  # noqa
        return os.path.join(self.ProjectRoot, "styles")

    @property
    def AppDataRoot(self):  # noqa
        # We need to have fallback value for APPDATA token, since
        # when tests are executed on Linux environment it would fail.
        return os.path.join(os.getenv("APPDATA") or "", "SaveGem")

    @property
    def Output(self):  # noqa
        return os.path.join(self.AppDataRoot, "Output")

    @property
    def Logs(self):  # noqa
        return os.path.join(self.AppDataRoot, "Logs")

    @property
    def Logback(self):  # noqa
        return os.path.join(self.AppDataRoot, "Logback")


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
    NotificationIco: Final = "notification.svg"
    ConfirmationIco: Final = "confirmation.svg"


JSON_EXTENSION: Final = ".json"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"
JSON_MIME_TYPE: Final = "application/json"

UTF_8: Final = "utf-8"
SHA_256: Final = "sha256"
