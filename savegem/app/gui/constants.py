from typing import Final


class UISection:
    """
    Represents UI sections that are
    being built by widget manager.
    """

    """
    Root section name.
    This is main section that is being built in the first
    place when application starts.
    """
    RootSection: Final = "root"

    """
    Section that should be displayed when data to present root
    section is still not available.
    """
    WaitSection: Final = "wait"

    """
    Section containing main application screen.
    """
    HomeSection: Final = "home"

    """
    Notification dialog section
    """
    NotificationSection: Final = "notification"

    """
    Confirmation dialog section
    """
    ConfirmationSection: Final = "confirmation"


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


"""
Used to transform regular boolean value
into QSS compatible.
"""
QBool: Final = lambda value: "true" if value else "false"


class QAttr:
    """
    Contains names of QT properties
    used in QSS.
    """

    Id: Final = "id"
    Kind: Final = "kind"
    Disabled: Final = "is-disabled"
