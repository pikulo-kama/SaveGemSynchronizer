import os
import re
from typing import Final, Optional

from constants import Directory, File
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import read_file, resolve_config, resolve_resource
from savegem.common.util.graphics import get_color_mode
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
_styles: Optional[JsonConfigHolder] = None

_FONTS_PROP: Final = "fonts"
_COLORS_PROP: Final = "colors"
_IMAGES_PROP: Final = "images"

_COLOR_MODE_LIGHT: Final = "light"
_COLOR_MODE_DARK: Final = "dark"


def _get_styles():
    """
    Internal method used to get styles configuration.
    """

    global _styles

    if _styles is None:
        _styles = JsonConfigHolder(resolve_config(File.Style))

    return _styles


def color(property_name: str):
    """
    Used to get color that corresponds
    provided property.

    Will get property depending on system color scheme.
    """

    color_mode = get_color_mode()
    colors = _get_styles().get_value(_COLORS_PROP).get(color_mode)
    return colors.get(property_name)


def font(property_name: str):
    """
    Used to get font that corresponds
    provided property.
    """
    return _get_styles().get_value(_FONTS_PROP).get(property_name)


def _resolve_style_properties(style_string: str):
    """
    Used to resolve color/font
    properties in string.
    """

    # Resolve colors.
    style_string = re.sub(
        r"color\(['\"]([^'\"]+)['\"]\)",
        lambda match: color(match.group(1)),
        style_string
    )

    # Resolve fonts.
    style_string = re.sub(
        r"font\(['\"]([^'\"]+)['\"]\)",
        lambda match: font(match.group(1)),
        style_string
    )

    # Resolve images.
    style_string = re.sub(
        r"image\(['\"]([^'\"]+)['\"]\)",
        lambda match: f"url('{resolve_resource(match.group(1)).replace(os.path.sep, "/")}')",
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
    for style in os.listdir(Directory().Styles):
        style_path = os.path.join(Directory().Styles, style)
        style_string += read_file(style_path)

    return _resolve_style_properties(style_string)
