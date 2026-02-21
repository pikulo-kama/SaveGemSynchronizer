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
    AppSettings: Final[str] = "appSettings"

class UIRefreshEvent:
    """
    Represents UI refresh event.
    """

    LanguageChange: Final[str] = "language_change"
    """
    Fired when the application language is toggled to refresh localized text.
    """

    ActivityLogUpdate: Final[str] = "activity_log_update"
    """
    Triggered when new entries are added to the activity holder object.
    """

    GameConfigChange: Final[str] = "game_config_change"
    """
    Signals game settings file have been modified.
    """

    AppSettingsChange: Final[str] = "app_settings_change"
    """
    Signals app settings file have been modified.
    """

    CloudSaveFilesChange: Final[str] = "cloud_files_change"
    """
    Triggered when there is a change in game save files on cloud.
    """

    GameSelectionChange: Final[str] = "game_selection_change"
    """
    Fired when the user selects a different game within the UI.
    """

    SaveDownloaded: Final[str] = "save_downloaded"
    """
    Signals that a save file download from the cloud has successfully completed.
    """

    LocalStoragePathChange: Final[str] = "local_storage_path_change"
    """
    Fired when the local data storage path for current game has changed.
    """


class File:
    """
    Contains names of files that are created/used by application.
    """

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
