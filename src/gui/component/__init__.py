

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
