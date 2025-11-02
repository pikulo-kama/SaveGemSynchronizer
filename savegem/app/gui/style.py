import os
import re
from typing import Optional

from constants import Directory, File
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.db.manager import db
from savegem.common.util.file import read_file, resolve_config, resolve_resource, save_file, resolve_temp_resource
from savegem.common.util.logger import get_logger
from savegem.common.util.ui import get_color_mode

_logger = get_logger(__name__)
_styles: Optional[JsonConfigHolder] = None


def _get_styles():
    """
    Internal method used to get styles configuration.
    """

    global _styles

    if _styles is None:
        _styles = JsonConfigHolder(resolve_config(File.Style))

    return _styles


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

    return f"rgba({red}, {green}, {blue}, {alpha})"


def color(property_name: str):
    """
    Used to get color that corresponds
    provided property.

    Will get property depending on system color scheme.
    """

    color_mode = get_color_mode()
    colors = _get_styles().get_value("colors").get(color_mode)
    return colors.get(property_name)


def font(property_name: str):
    """
    Used to get font that corresponds
    provided property.
    """
    return _get_styles().get_value("fonts").get(property_name)


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

    if not os.path.exists(Directory().TempResources):
        os.mkdir(Directory().TempResources)

    resources = db().table("setup_resource")

    for resource in resources.retrieve():
        name = resource.get("resource_name")
        file_name = resource.get("resource_path")
        current_color = resource.get("color")
        resolved_color = color(current_color)

        if resolved_color is not None:
            current_color = resolved_color

        resource_content = read_file(resolve_resource(file_name, include_temporary=False))

        if current_color is not None:
            resource_content = resource_content.replace("currentColor", current_color)

        save_file(resolve_temp_resource(name), resource_content)
