from typing import Final


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
    SizeVariant: Final = "variant"
    Disabled: Final = "is-disabled"


class QObjectName:
    """
    Contains names of QSS objects.
    """

    Button: Final = "button"
    Chip: Final = "chip"
    ComboBox: Final = "comboBox"
    SquareButton: Final = "squareButton"


class QSizeVariant:
    """
    Contains names of QT size variants.
    """

    Small: Final = "small"


class QKind:
    """
    Contains names of element kinds.
    """

    Primary: Final = "primary"
    Secondary: Final = "secondary"
    Disabled: Final = "disabled"
