from typing import Final


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
    FgColor: Final = "foreground"
    BgColor: Final = "background"
    Radius: Final = "radius"
    Progress: Final = "progress"


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


class TkCursor:
    """
    Contains Tkinter cursor names.
    """

    Default: Final = ""
    Wait: Final = "wait"
    Hand: Final = "hand2"
    Forbidden: Final = "no"
