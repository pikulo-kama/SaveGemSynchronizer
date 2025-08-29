import tkinter as tk
from tkinter import font

from src.gui.component import safe_delete_props, unwrap_paddings, parse_font, safe_get_prop
from src.gui.style import style, adjust_color

_STYLE_PROP = "style"
_TEXT_PROP = "text"
_PROGRES_PROP = "progress"
_COMMAND_PROP = "command"
_WIDTH_PROP = "width"
_HEIGHT_PROP = "height"


# TODO: Not really fond of this class... Need to think of the way to reorganize it.

class ProgressButton(tk.Frame):
    """
    Button component that allows to set progress property
    which could emulate progress bar animation on button.
    """

    def __init__(self, master, **kwargs):

        self.__text = ""
        self.__progress = None
        self.__command = None
        self.__width = None
        self.__height = None

        kwargs = self.__initialize(**kwargs)
        super().__init__(master, **kwargs)

        self.__canvas = tk.Canvas(self, highlightthickness=0)
        self.__canvas.pack(fill="both", expand=True)

        self.__bind_command()
        self.__draw()

    def configure(self, cnf=None, **kwargs):

        kwargs = self.__initialize(**kwargs)
        super().configure(cnf, **kwargs)

        self.__bind_command()
        self.__draw()

    def __draw(self):
        """
        Used to draw button on UI.
        """

        width = self.__get_width()
        height = self.__get_height()

        self.__canvas.delete("all")
        self.__canvas.configure(width=width, height=height)

        # Draw button itself.
        self.__canvas.create_rectangle(
            0, 0, width, height,
            fill=self.__background,
            outline=""
        )

        # Add progres bar on top.
        if self.__progress is not None:
            self.__canvas.create_rectangle(
                0, 0, width * self.__progress, height,
                fill=adjust_color(self.__background, 0.95),
                outline=""
            )

        # Draw text on top of button.
        self.__canvas.create_text(
            width / 2, height / 2,
            text=self.__text,
            fill=self.__foreground,
            font=self.__font
        )

    def __initialize(self, **kwargs):
        """
        Used to initialize custom component properties.
        Will only overwrite existing value if it's not None.
        """

        text = safe_get_prop(_TEXT_PROP, **kwargs)
        progress = safe_get_prop(_PROGRES_PROP, **kwargs)
        command = safe_get_prop(_COMMAND_PROP, **kwargs)
        style_name = safe_get_prop(_STYLE_PROP, **kwargs)

        if style_name is not None:
            self.__init_style(style_name)

        if text is not None:
            self.__text = text

        if progress is not None:
            self.__progress = progress

        if command is not None:
            self.__command = command

        # Ensure font/paddings/colors are initialized at least once
        if self.__font is None:
            self.__font = font.nametofont("TkDefaultFont")

        if self.__paddings is None:
            self.__paddings = (0, 0, 0, 0)

        if self.__foreground is None:
            self.__foreground = "black"

        if self.__background is None:
            self.__background = "white"

        width = safe_get_prop(_WIDTH_PROP, **kwargs)
        height = safe_get_prop(_HEIGHT_PROP, **kwargs)

        if width is not None:
            self.__width = width

        if self.__width is None:
            self.__width = self.__font.measure(self.__text)

        if height is not None:
            self.__height = height

        if self.__height is None:
            self.__height = 1

        # Remove custom properties before passing kwargs to parent class.
        return safe_delete_props([_STYLE_PROP, _TEXT_PROP, _PROGRES_PROP, _COMMAND_PROP], **kwargs)

    def __bind_command(self):
        """
        Used to bind left mouse button command.
        """

        self.__canvas.unbind("<Button-1>")

        if self.__command is not None:
            self.__canvas.bind("<Button-1>", lambda _: self.__command())

    def __init_style(self, style_name: str):
        """
        Used to initialize properties from provided style.
        """

        if style_name is None:
            return

        self.__font = font.Font(root=None, font=parse_font(style.lookup(style_name, "font")))
        self.__paddings = unwrap_paddings(style.lookup(style_name, "padding"))
        self.__foreground = style.lookup(style_name, "foreground")
        self.__background = style.lookup(style_name, "background")

    def __get_width(self):
        """
        Used to get true width of button.
        Takes into consideration paddings.
        """

        p_left, _, p_right, _ = self.__paddings
        width = self.__font.measure(self.__text)

        if self.__width is not None:
            width = self.__font.measure("0") * self.__width

        return width + p_left + p_right

    def __get_height(self):
        """
        Used to get true height of button.
        Takes into consideration paddings.
        """

        _, p_top, _, p_bottom = self.__paddings
        return self.__height * self.__font.metrics("linespace") + p_top + p_bottom
