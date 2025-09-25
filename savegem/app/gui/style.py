import os
import re
from typing import Final

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from constants import Directory, File
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import read_file, resolve_config
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
_styles = JsonConfigHolder(resolve_config(File.Style))

_FONTS_PROP: Final = "fonts"
_COLORS_PROP: Final = "colors"

_COLOR_MODE_LIGHT: Final = "light"
_COLOR_MODE_DARK: Final = "dark"


def _color(property_name: str):
    """
    Used to get color that corresponds
    provided property.

    Will get property depending on system color scheme.
    """

    mode = _COLOR_MODE_LIGHT
    color_scheme = QApplication.instance().styleHints().colorScheme()  # noqa

    if color_scheme == Qt.ColorScheme.Light:
        mode = _COLOR_MODE_LIGHT

    elif color_scheme == Qt.ColorScheme.Dark:
        mode = _COLOR_MODE_DARK

    colors = _styles.get_value(_COLORS_PROP).get(mode)
    return colors.get(property_name)


def _font(property_name: str):
    """
    Used to get font that corresponds
    provided property.
    """
    return _styles.get_value(_FONTS_PROP).get(property_name)


def resolve_style_properties(style_string: str):
    """
    Used to resolve color/font
    properties in string.
    """

    # Resolve colors.
    style_string = re.sub(
        r"color\(['\"]([^'\"]+)['\"]\)",
        lambda match: _color(match.group(1)),
        style_string
    )

    # Resolve fonts.
    style_string = re.sub(
        r"font\(['\"]([^'\"]+)['\"]\)",
        lambda match: _font(match.group(1)),
        style_string
    )

    return style_string


def load_stylesheet():
    """
    Used to load all stylesheets and combine
    them into single string.
    """

    style_string = ""

    # Get all style files and join them together.
    for style in os.listdir(Directory.Styles):
        style_path = os.path.join(Directory.Styles, style)
        style_string += read_file(style_path)

    return resolve_style_properties(style_string)
