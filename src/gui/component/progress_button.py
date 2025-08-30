from src.gui.component.button import Button
from src.gui.constants import TkAttr
from src.gui.style import adjust_color
from src.util.graphics import create_polygon


class ProgressButton(Button):
    """
    Button component that allows to set progress property
    which could emulate progress bar animation on button.
    """

    def _draw_on_body(self):

        progress = self._get_value(TkAttr.Progress)

        # Only draw is progress greater than 0.
        if progress is None or progress == 0:
            return

        width = self._get_width()
        height = self._get_height()
        radius = self._get_value(TkAttr.Radius)
        background = self._get_value(TkAttr.BgColor)

        create_polygon(
            0, 0, width * progress, height,
            widget=self._canvas,
            radius=radius,
            fill=adjust_color(background, 0.95),
            outline=""
        )
