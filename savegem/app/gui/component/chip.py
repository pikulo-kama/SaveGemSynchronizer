import tkinter as tk

from PIL import ImageTk

from savegem.app.gui.component import Component
from savegem.app.gui.constants import TkAttr
from savegem.common.util.graphics import create_round_image


class Chip(Component):
    """
    Custom Tkinter chip component.
    Allows to draw rectangle with image and text inside it.
    """

    def _do_draw(self):
        m_left, _, m_right, _ = self._get_margin()

        width = self._get_width()
        height = self._get_height()
        text = self._get_value(TkAttr.Text)
        font = self._get_font()

        foreground = self._get_value(TkAttr.FgColor)
        background = self._get_value(TkAttr.BgColor)
        image_path = self._get_value(TkAttr.Image)

        image = create_round_image(image_path, background, int(height * .7))
        tk_image = ImageTk.PhotoImage(image)

        image_width = tk_image.width()
        text_width = font.measure(text)

        components_width = image_width + text_width

        # Gap is what free space is left when we take margins into consideration.
        gap = (width - components_width) - m_left - m_right

        # Draw chip image.
        self._canvas.create_image(
            m_left + image_width / 2,
            height / 2,
            image=tk_image,
            anchor=tk.CENTER
        )
        self._canvas.image = tk_image

        # Draw chip label.
        self._canvas.create_text(
            m_left + image_width + gap + text_width / 2,
            height / 2,
            text=text,
            font=font,
            fill=foreground
        )
