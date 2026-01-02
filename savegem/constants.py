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

    RootSection: Final[str] = "root"
    """
    Root section name.
    This is main section that is being built in the first
    place when application starts.
    """

    WaitSection: Final[str] = "wait"
    """
    Section that should be displayed when data to present root
    section is still not available.
    """

    HomeSection: Final[str] = "home"
    """
    Section containing main application screen.
    """

    NotificationSection: Final[str] = "notification"
    """
    Notification dialog section
    """

    ConfirmationSection: Final[str] = "confirmation"
    """
    Confirmation dialog section
    """


class UIRefreshEvent:
    """
    Represents UI refresh event.
    """

    All: Final[str] = "all"

    LanguageChange: Final[str] = "language_change"
    ActivityLogUpdate: Final[str] = "activity_log_update"
    GameConfigChange: Final[str] = "game_config_change"
    CloudSaveFilesChange: Final[str] = "cloud_files_change"
    GameSelectionChange: Final[str] = "game_selection_change"
    SaveDownloaded: Final[str] = "save_downloaded"
    MenuItemChanged: Final[str] = "menu_item_changed"


class File:
    """
    Contains names of files that are created/used by application.
    """

    GDriveToken: Final[str] = "token.json"
    GDriveCreds: Final[str] = "credentials.json"
    GDriveConfig: Final[str] = "config.json"


class TimeFormat:
    """
    Contains list of supported time formats.
    """

    Regular: Final[int] = 0
    """
    12-hour format
    """

    Military: Final[int] = 1
    """
    24-hour format.
    """
