import tkinter as tk
from tkinter import font
from tkinter.ttk import Style
from src.core.holders import prop
from src.util.logger import get_logger

_logger = get_logger(__name__)


def init_gui_styles():
    """
    Used to initialize Tkinter custom styles.
    """

    style = Style()
    style.theme_use("clam")

    add_button(style, "primaryButton")
    add_button(style, "secondaryButton")

    add_small_button(style, "primaryButton")
    add_small_button(style, "secondaryButton")

    for font_size in [16, 18]:
        add_square_button(style, "primaryButton", font_size)
        add_square_button(style, "secondaryButton", font_size)

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
        fieldbackground=expand_property(prop("secondaryButton.colorHover")),
        selectbackground=expand_property(prop("secondaryButton.colorHover")),
        foreground=expand_property(prop("secondaryColor")),
        selectforeground=expand_property(prop("secondaryColor")),
        background=expand_property(prop("secondaryButton.colorStatic"))
    )


def add_button(style: Style, button: str):
    """
    Used to create regular button style using provided configuration.
    """

    style_name = f"{prop(f"{button}.styleName")}.TButton"
    log_style(style_name)

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


def add_small_button(style: Style, button):
    """
    Used to create small button style using provided configuration.
    """

    style_name = f"Small{prop(f"{button}.styleName")}.TButton"
    log_style(style_name)

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


def add_square_button(style: Style, button, font_size: int):
    """
    Used to create square button style using provided configuration and font size.
    """

    style_name = f"Square{prop(f"{button}.styleName")}.{font_size}.TButton"
    log_style(style_name)

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
        background=[
            ("active", prop(f"{button}.colorHover")),
            ("pressed", prop(f"{button}.colorStatic"))
        ]
    )


def add_button_movement_effect(button, pixel_offset=2):
    """
    Used to add elevation effect to button when it's being clicked.
    """

    original_y = button.winfo_y()

    button.bind("<ButtonPress-1>", lambda e: e.widget.place_configure(y=original_y + pixel_offset))
    button.bind("<ButtonRelease-1>", lambda e: e.widget.place_configure(y=original_y - pixel_offset))


def log_style(style_name: str):
    """
    Just a wrapper to log event when custom style is being registered.
    """
    _logger.info("Adding custom style '%s'", style_name)


def expand_property(value):
    """
    Used to create tuple list for value.
    Needed for scenarios where property should be the same
    regardless of current state.
    """
    return [("readonly", value), ("disabled", value)]
