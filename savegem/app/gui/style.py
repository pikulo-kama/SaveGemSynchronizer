import os
import re
from pathlib import Path
from typing import Optional, Final

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from constants import Directory
from savegem.common.core.context import app
from savegem.common.db.manager import db
from savegem.common.db.table import DatabaseTable
from savegem.common.util.file import read_file, resolve_resource, save_file, resolve_temp_resource
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)
_colors: Optional[DatabaseTable] = None
_fonts: dict[str, str] = {}


class ColorMode:
    """
    Represents application color modes.
    """

    Light: Final = "light"
    Dark: Final = "dark"


def get_system_color_mode():
    """
    Used to get current color mode.
    """

    mode = ColorMode.Light
    application = QApplication.instance()

    if application is None:
        return mode

    color_scheme = application.styleHints().colorScheme()  # noqa

    if color_scheme == Qt.ColorScheme.Dark:
        mode = ColorMode.Dark

    return mode


def _get_colors():
    """
    Used to load colors data from database.
    """

    global _colors

    if _colors is None:
        _colors = db().retrieve_table("setup_color")

    return _colors


def _get_fonts():
    """
    Used to load fonts from database
    and format them.
    """

    global _fonts

    if len(_fonts) == 0:

        for font_record in db().retrieve_table("setup_font"):
            font_id = font_record.get("font_id")
            font_size = font_record.get("font_size")
            font_family = font_record.get("font_family")
            font_weight = font_record.get("font_weight") or 400

            _fonts[font_id] = f"{font_size}px '{font_family}'; font-weight: {font_weight}"

    return _fonts


def rgba_color(color_key: str, alpha: str):
    """
    Used to get unwrap color property
    and transform it from hexadecimal format
    into decimal.
    """

    color_hex = color(color_key)
    red = int(color_hex[1:3], 16)
    green = int(color_hex[3:5], 16)
    blue = int(color_hex[5:7], 16)

    color_rgba = f"rgba({red}, {green}, {blue}, {alpha})"
    _logger.debug("Transformed color key '%s' with alpha %s into RGBA = '%s'", color_key, alpha, color_rgba)

    return color_rgba


def color(color_id: str):
    """
    Used to get color that corresponds
    provided property.

    Will get property depending on system color scheme.s
    """

    color_mode = app().state.color_theme
    color_hex = ""

    if color_mode is None:
        color_mode = get_system_color_mode()

    for color_record in _get_colors():
        if color_id == color_record.get("color_id"):
            color_hex = color_record.get(color_mode)
            break

    _logger.debug("Resolved color with ID %s to %s", color_id, color_hex)
    return color_hex


def font(property_name: str):
    """
    Used to get font that corresponds
    provided property.
    """
    return _get_fonts().get(property_name)


def resolve_style_properties(style_string: str):
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

    # Resolve RGBA colors.
    style_string = re.sub(
        r"rgba\(\s*['\"]([^'\"]+)['\"]\s*,\s*([^)]+)\s*\)",
        lambda match: rgba_color(match.group(1), match.group(2)),
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

    _logger.debug("Resolved stylesheet: %s", style_string)
    return style_string


def load_stylesheet(directory: str = None):
    """
    Used to load all stylesheets and combine
    them into single string.

    Will also load styles from nested directories.
    """

    style_string = ""

    if directory is None:
        directory = Directory().Styles

    # Get all style files and join them together.
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        if Path(file_path).is_dir():
            style_string += load_stylesheet(file_path)
        else:
            style_string += read_file(file_path)

    return resolve_style_properties(style_string)


def create_dynamic_resources():
    """
    Used to create dynamic resources.
    Mainly this applies to SVG elements
    that are just an XML files where we can
    replace colors.

    This is needed in the first place to avoid
    creating duplicate resources where the only
    difference is color.
    """

    _logger.debug("Creating dynamic resources.")
    for resource in db().retrieve_table("setup_resource"):
        name = resource.get("resource_name")
        file_name = resource.get("resource_path")
        current_color = resource.get("color")
        resolved_color = color(current_color)

        if resolved_color is not None:
            current_color = resolved_color

        resource_content = read_file(resolve_resource(file_name, include_temporary=False))

        if current_color is not None:
            resource_content = resource_content.replace("currentColor", current_color)

        _logger.debug("Creating resource %s using color %s", name, current_color)
        save_file(resolve_temp_resource(name), resource_content)
