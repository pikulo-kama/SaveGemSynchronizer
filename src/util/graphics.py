
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
