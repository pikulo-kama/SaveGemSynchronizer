from typing import Final


class HolderObject:
    """
    Object names that are being stored
    in data holder.
    """

    CurrentUser: Final[str] = "currentUser"
    AllUsers: Final[str] = "allUsers"
    UserData: Final[str] = "userData"

    Activity: Final[str] = "activity"
    GamesConfig: Final[str] = "gamesConfig"


class UISection:
    """
    Represents UI sections that are
    being built by widget manager.
    """

    RootSection: Final = "root"
    """
    Root section name.
    This is main section that is being built in the first
    place when application starts.
    """

    WaitSection: Final = "wait"
    """
    Section that should be displayed when data to present root
    section is still not available.
    """

    HomeSection: Final = "home"
    """
    Section containing main application screen.
    """

    NotificationSection: Final = "notification"
    """
    Notification dialog section
    """

    ConfirmationSection: Final = "confirmation"
    """
    Confirmation dialog section
    """


class UIRefreshEvent:
    """
    Represents UI refresh event.
    """

    All: Final = "all"

    LanguageChange: Final = "language_change"
    ActivityLogUpdate: Final = "activity_log_update"
    GameConfigChange: Final = "game_config_change"
    CloudSaveFilesChange: Final = "cloud_files_change"
    GameSelectionChange: Final = "game_selection_change"
    SaveDownloaded: Final = "save_downloaded"
    MenuItemChanged: Final = "menu_item_changed"


class File:
    """
    Contains names of files that are created/used by application.
    """

    GDriveToken: Final = "token.json"
    GDriveCreds: Final = "credentials.json"
    GDriveConfig: Final = "config.json"
    AppConfig: Final = "app.json"


class Resource:
    """
    Contains name of resource files
    """

    ApplicationIco: Final = "application.ico"
    NotificationIco: Final = "notification.svg"
    ConfirmationIco: Final = "confirmation.svg"


class TimeFormat:
    """
    Contains list of supported time formats.
    """

    """
    12-hour format
    """
    Regular: Final = 0

    """
    24-hour format.
    """
    Military: Final = 1


JSON_EXTENSION: Final = ".json"
JPG_EXTENSION: Final = ".jpg"
ZIP_EXTENSION: Final = "zip"
ZIP_MIME_TYPE: Final = "application/zip"
JSON_MIME_TYPE: Final = "application/json"

UTF_8: Final = "utf-8"
SHA_256: Final = "sha256"
