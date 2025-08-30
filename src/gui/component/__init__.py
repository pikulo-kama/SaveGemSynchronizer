import tkinter as tk


def safe_get_prop(prop_name: str, default=None, **kw):
    if prop_name not in kw:
        return default

    return kw[prop_name]


def safe_delete_props(prop_list: list[str], **kwargs):

    for prop in prop_list:
        if prop in kwargs:
            del kwargs[prop]

    return kwargs


def unwrap_paddings(pad):

    if type(pad) is int:
        # Single value for all sides.
        return pad, pad, pad, pad

    if pad is None or len(pad) == 0:
        return 0, 0, 0, 0

    elif len(pad) == 2:
        return pad[0], pad[1], pad[0], pad[1]

    elif len(pad) == 4:
        return pad


def parse_font(font_str: str):

    font_name_start = font_str.index("{")
    font_name_end = font_str.index("}")

    font_name = font_str[font_name_start + 1:font_name_end]
    font_parts = str(font_str[font_name_end + 1:]).strip().split(" ")

    if len(font_parts) == 1:
        return font_name, int(font_parts[0])

    if len(font_parts) > 1:
        return font_name, int(font_parts[0]), font_parts[1]

    return font_name


class Component(tk.Frame):

    def create_polygon(self, x1, y1, width, height, radius=0, widget=None, **kw):

        x2 = x1 + width
        y2 = y1 + height

        points = [
            # Bottom left
            x1 + radius, y1,
            x1, y1,
            x1, y1 + radius,

            # Top left
            x1, y2 - radius,
            x1, y2,
            x1 + radius, y2,

            # Top right
            x2 - radius, y2,
            x2, y2,
            x2, y2 - radius,

            # Bottom right
            x2, y1 + radius,
            x2, y1,
            x2 - radius, y1
        ]

        if widget is None:
            widget = self

        return widget.create_polygon(points, smooth=True, **kw)
