from PIL import Image, ImageDraw


def create_polygon(x1, y1, width, height, radius, widget, **kw):
    """
    Used to draw polygon with rounded corners.
    """

    if widget is None or radius is None:
        return None

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

    return widget.create_polygon(points, smooth=True, **kw)


def create_round_image(image_path: str, background_color: str, size: int):
    """
    Used to create rounded image.
    Uses super sampling to achieve higher image quality.
    """

    original_size = int(size)
    size *= 4

    # Load and resize the image.
    image = Image.open(image_path) \
        .convert("RGBA") \
        .resize((size, size), Image.Resampling.LANCZOS)

    # Create background.
    background_tuple = tuple(int(background_color[idx:idx + 2], 16) for idx in (1, 3, 5)) + (255,)
    background = Image.new("RGBA", (size, size), background_tuple)

    # Create circular mask.
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask) \
        .ellipse((0, 0, size - 1, size - 1), fill=255)

    return Image.composite(image, background, mask) \
        .resize((original_size, original_size), Image.Resampling.LANCZOS)
