import tkinter as tk
from tkinter import font
from tkinter.ttk import Style
from savegem.common.core.holders import prop
from savegem.app.gui.constants import TkState, TkCursor
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
style = Style()


def adjust_color(hex_color: str, factor: float) -> str:
    """
    Darken or brighter a HEX color by a given factor (0–1).
    Example: adjust_color("#6699ff", 0.8) -> "#527acc"
    """

    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)

    return f"#{r:02x}{g:02x}{b:02x}"


def init_gui_styles():
    """
    Used to initialize Tkinter custom styles.
    """

    style.theme_use("clam")

    _add_button("primaryButton")
    _add_button("secondaryButton")

    _add_small_button("primaryButton")
    _add_small_button("secondaryButton")

    for font_size in [10, 18]:
        _add_square_button("primaryButton", font_size)
        _add_square_button("secondaryButton", font_size)

    _add_secondary_dropdown()
    _add_secondary_chip()


def _add_secondary_dropdown():
    """
    Used to add custom Combobox styles with secondary color accent.
    """

    dropdown_style = "Secondary.TDropdown"
    listbox_style = dropdown_style + ".TListbox"

    _log_style(dropdown_style)
    _log_style(listbox_style)

    style.configure(
        dropdown_style,
        background=prop("secondaryButton.colorStatic"),
        foreground=prop("primaryColor"),
        font=("Segoe UI Semibold", 10, font.BOLD),
        cursor=TkCursor.Hand,
        radius=6,
        padding=5
    )

    style.configure(
        listbox_style,
        background=prop("secondaryButton.colorStatic"),
        foreground=prop("primaryColor"),
        font=("Segoe UI Semibold", 8, font.BOLD),
        cursor=TkCursor.Hand,
        padding=5
    )

    style.map(
        dropdown_style,
        background=_expand_property(prop("secondaryButton.colorStatic"))
    )

    style.map(
        listbox_style,
        background=[
            (TkState.Active, prop("primaryButton.colorHover")),
            (TkState.Pressed, prop("secondaryButton.colorStatic"))
        ]
    )


def _add_secondary_chip():
    """
    Used to add secondary style to custom Chip component.
    """

    style_name = "Primary.TChip"
    _log_style(style_name)

    style.configure(
        style_name,
        height=2,
        radius=5,
        font=("Segoe UI Semibold", 10),
        foreground=prop("primaryColor"),
        background=prop("primaryButton.colorStatic")
    )


def _add_button(button: str):
    """
    Used to create regular button style using provided configuration.
    """

    style_name = f"{prop(f"{button}.styleName")}.TButton"
    _log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        foreground=prop("primaryColor"),
        background=prop(f"{button}.colorStatic"),
        padding=(18, 20),
        cursor=TkCursor.Hand,
        font=("Segoe UI Semibold", 18),
        radius=10
    )

    style.map(
        style_name,
        background=[
            (TkState.Active, prop(f"{button}.colorHover")),
            (TkState.Pressed, prop(f"{button}.colorStatic"))
        ]
    )


def _add_small_button(button):
    """
    Used to create small button style using provided configuration.
    """

    style_name = f"Small{prop(f"{button}.styleName")}.TButton"
    _log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        foreground=prop("primaryColor"),
        background=prop(f"{button}.colorStatic"),
        padding=8,
        cursor=TkCursor.Hand,
        font=12,
        radius=3
    )

    style.map(
        style_name,
        background=[
            (TkState.Active, prop(f"{button}.colorHover")),
            (TkState.Pressed, prop(f"{button}.colorStatic"))
        ]
    )


def _add_square_button(button, font_size: int):
    """
    Used to create square button style using provided configuration and font size.
    """

    style_name = f"Square{prop(f"{button}.styleName")}.{font_size}.TButton"
    _log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        font=("Small Fonts", font_size, font.BOLD),
        width=3,
        height=1,
        foreground=prop("primaryColor"),
        background=prop(f"{button}.colorStatic"),
        padding=(8, 12),
        cursor=TkCursor.Hand,
        radius=5,
    )

    style.map(
        style_name,
        foreground=_expand_property(prop("primaryColor")),
        background=[
            (TkState.Active, prop(f"{button}.colorHover")),
            (TkState.Pressed, prop(f"{button}.colorStatic"))
        ]
    )


def _expand_property(value):
    """
    Used to create tuple list for value.
    Needed for scenarios where property should be the same
    regardless of current state.
    """
    return [(TkState.Readonly, value), (TkState.Disabled, value)]


def _log_style(style_name: str):
    """
    Just a wrapper to log event when custom style is being registered.
    """
    _logger.info("Adding custom style '%s'", style_name)
