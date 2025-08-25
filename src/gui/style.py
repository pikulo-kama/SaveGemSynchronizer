import tkinter as tk
from tkinter import font
from tkinter.ttk import Style
from src.core.holders import prop
from src.util.logger import get_logger

logger = get_logger(__name__)


def init_styles():
    """
    Used to initialize Tkinter custom styles.
    """

    style = Style()
    style.theme_use("clam")

    add_button(style, prop("primaryButton"))
    add_button(style, prop("secondaryButton"))

    add_small_button(style, prop("primaryButton"))
    add_small_button(style, prop("secondaryButton"))

    for font_size in [16, 18]:
        add_square_button(style, prop("primaryButton"), font_size)
        add_square_button(style, prop("secondaryButton"), font_size)

    add_secondary_combobox(style)


def add_secondary_combobox(style: Style):
    """
    Used to add custom Combobox styles with secondary color accent.
    """

    style_name = "Secondary.TCombobox"
    log_style(style_name)

    style.configure(
        style_name,
        padding=(10, 0, 0, 0)
    )

    style.map(
        style_name,
        fieldbackground=expand_property(prop("secondaryButton")["colorHover"]),
        selectbackground=expand_property(prop("secondaryButton")["colorHover"]),
        foreground=expand_property(prop("secondaryColor")),
        selectforeground=expand_property(prop("secondaryColor")),
        background=expand_property(prop("secondaryButton")["colorStatic"])
    )


def add_button(style: Style, button):
    """
    Used to create regular button style using provided configuration.
    """

    style_name = f"{button["styleName"]}.TButton"
    log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        foreground=prop("primaryColor"),
        background=button["colorStatic"],
        padding=(15, 15),
        font=40
    )

    style.map(
        style_name,
        background=[
            ("active", button["colorHover"]),
            ("pressed", button["colorStatic"])
        ]
    )


def add_small_button(style: Style, button):
    """
    Used to create small button style using provided configuration.
    """

    style_name = f"Small{button["styleName"]}.TButton"
    log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        foreground=prop("secondaryColor"),
        background=button["colorStatic"],
        padding=(5, 5),
        font=4
    )

    style.map(
        style_name,
        background=[
            ("active", button["colorHover"]),
            ("pressed", button["colorStatic"])
        ]
    )


def add_square_button(style: Style, button, font_size: int):
    """
    Used to create square button style using provided configuration and font size.
    """

    style_name = f"Square{button["styleName"]}.{font_size}.TButton"
    log_style(style_name)

    style.configure(
        style_name,
        borderwidth=0,
        relief=tk.SOLID,
        font=("Small Fonts", font_size, font.BOLD),
        width=3,
        height=1,
        foreground=prop("primaryColor"),
        background=button["colorStatic"],
        padding=(7, 10)
    )

    style.map(
        style_name,
        background=[
            ("active", button["colorHover"]),
            ("pressed", button["colorStatic"])
        ]
    )


def log_style(style_name: str):
    """
    Just a wrapper to log event when custom style is being registered.
    """
    logger.info("Adding custom style '%s'", style_name)


def expand_property(value):
    """
    Used to create tuple list for value.
    Needed for scenarios where property should be the same
    regardless of current state.
    """
    return [("readonly", value), ("disabled", value)]
