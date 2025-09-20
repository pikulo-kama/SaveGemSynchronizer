from typing import Final


class UIRefreshEvent:
    """
    Represents UI refresh event.
    """

    Always: Final = "always"

    LanguageChange: Final = "language_change"
    ActivityLogUpdate: Final = "activity_log_update"
    GameConfigChange: Final = "game_config_change"
    CloudSaveFilesChange: Final = "cloud_files_change"
    GameSelectionChange: Final = "game_selection_change"
    AfterUploadDownloadComplete: Final = "after_upload_download"


class TkAttr:
    """
    Contains names of built-in and custom
    Tkinter component attributes.
    """

    Style: Final = "style"
    State: Final = "state"
    Text: Final = "text"
    Font: Final = "font"
    Command: Final = "command"
    Width: Final = "width"
    Height: Final = "height"
    Padding: Final = "padding"
    Margin: Final = "margin"
    FgColor: Final = "foreground"
    BgColor: Final = "background"
    Radius: Final = "radius"
    Progress: Final = "progress"
    Image: Final = "image"
    Values: Final = "values"
    Prefix: Final = "prefix"


class TkState:
    """
    Contains Tkinter component states.
    """

    Default: Final = ""
    Active: Final = "active"
    Pressed: Final = "pressed"
    Disabled: Final = "disabled"
    Readonly: Final = "readonly"


class TkEvent:
    """
    Contains Tkinter component event names.
    """

    LMBClick: Final = "<Button-1>"
    LMBRelease: Final = "<ButtonRelease-1>"
    MoveResize: Final = "<Configure>"
    Enter: Final = "<Enter>"
    Leave: Final = "<Leave>"
    ComboboxSelected: Final = "<<ComboboxSelected>>"
    ListboxSelected: Final = "<<ListboxSelect>>"


class TkCursor:
    """
    Contains Tkinter cursor names.
    """

    Default: Final = ""
    Wait: Final = "wait"
    Hand: Final = "hand2"
    Forbidden: Final = "no"
