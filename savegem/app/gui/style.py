import os
import re
from typing import Final

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from constants import Directory, File
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import read_file, resolve_config, resolve_resource
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
_styles = JsonConfigHolder(resolve_config(File.Style))

_FONTS_PROP: Final = "fonts"
_COLORS_PROP: Final = "colors"
_IMAGES_PROP: Final = "images"

_COLOR_MODE_LIGHT: Final = "light"
_COLOR_MODE_DARK: Final = "dark"


def _color(property_name: str):
    """
    Used to get color that corresponds
    provided property.

    Will get property depending on system color scheme.
    """

    color_mode = _get_color_mode()
    colors = _styles.get_value(_COLORS_PROP).get(color_mode)
    return colors.get(property_name)


def _font(property_name: str):
    """
    Used to get font that corresponds
    provided property.
    """
    return _styles.get_value(_FONTS_PROP).get(property_name)


def _image(file_name: str):
    """
    Used to get image resource QSS token.
    Will use current color mode to resolve
    path to image.
    """

    color_mode = _get_color_mode()
    image_token = f"url('{resolve_resource(os.path.join(color_mode, file_name))}')"
    return image_token.replace(os.path.sep, '/')


def _get_color_mode():
    """
    Used to get current color mode.
    """

    mode = _COLOR_MODE_LIGHT
    color_scheme = QApplication.instance().styleHints().colorScheme()  # noqa

    if color_scheme == Qt.ColorScheme.Light:
        mode = _COLOR_MODE_LIGHT

    elif color_scheme == Qt.ColorScheme.Dark:
        mode = _COLOR_MODE_DARK

    return mode


def _resolve_style_properties(style_string: str):
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

    # Resolve images.
    style_string = re.sub(
        r"image\(['\"]([^'\"]+)['\"]\)",
        lambda match: _image(match.group(1)),
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

    return _resolve_style_properties(style_string)
