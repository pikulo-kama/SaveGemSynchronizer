import tkinter as tk
from tkinter import font
from tkinter.ttk import Style
from src.core.holders import prop
from src.util.logger import get_logger

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

    for font_size in [16, 18]:
        _add_square_button("primaryButton", font_size)
        _add_square_button("secondaryButton", font_size)

    _add_secondary_combobox()


def _add_secondary_combobox():
    """
    Used to add custom Combobox styles with secondary color accent.
    """

    style_name = "Secondary.TCombobox"
    _log_style(style_name)

    style.configure(
        style_name,
        padding=(10, 0, 0, 0)
    )

    style.map(
        style_name,
        fieldbackground=_expand_property(prop("secondaryButton.colorHover")),
        selectbackground=_expand_property(prop("secondaryButton.colorHover")),
        foreground=_expand_property(prop("secondaryColor")),
        selectforeground=_expand_property(prop("secondaryColor")),
        background=_expand_property(prop("secondaryButton.colorStatic"))
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
        padding=15,
        font=("Segoe UI Semibold", 15)
    )

    style.map(
        style_name,
        background=[
            ("active", prop(f"{button}.colorHover")),
            ("pressed", prop(f"{button}.colorStatic"))
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
        foreground=prop("secondaryColor"),
        background=prop(f"{button}.colorStatic"),
        padding=(5, 5),
        font=4
    )

    style.map(
        style_name,
        background=[
            ("active", prop(f"{button}.colorHover")),
            ("pressed", prop(f"{button}.colorStatic"))
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
        padding=(7, 10)
    )

    style.map(
        style_name,
        foreground=_expand_property(prop("primaryColor")),
        background=[
            ("active", prop(f"{button}.colorHover")),
            ("pressed", prop(f"{button}.colorStatic"))
        ]
    )


def _log_style(style_name: str):
    """
    Just a wrapper to log event when custom style is being registered.
    """
    _logger.info("Adding custom style '%s'", style_name)


def _expand_property(value):
    """
    Used to create tuple list for value.
    Needed for scenarios where property should be the same
    regardless of current state.
    """
    return [("readonly", value), ("disabled", value)]
