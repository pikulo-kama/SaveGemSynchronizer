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
_STATE_PROP = "state"


# TODO: Not really fond of this class... Need to think of the way to reorganize it.

class ProgressButton(tk.Frame):
    """
    Button component that allows to set progress property
    which could emulate progress bar animation on button.
    """

    def __init__(self, master, **kw):

        self.__state = ""
        self.__style_name = ""

        self.__text = ""
        self.__progress = None
        self.__command = None
        self.__width = None
        self.__height = None
        self.__is_disabled = False

        kw = self.__initialize(**kw)
        super().__init__(master, **kw)

        self.__canvas = tk.Canvas(self, highlightthickness=0)
        self.__canvas.pack(fill="both", expand=True)

        self.__register_handlers()
        self.__draw()

    def configure(self, cnf=None, **kw):

        kw = self.__initialize(**kw)
        super().configure(cnf, **kw)

        self.__register_handlers()
        self.__draw()

    def __draw(self):
        """
        Used to draw button on UI.
        """

        width = self.__get_width()
        height = self.__get_height()

        background = self.__get_style_value("background", "#ffffff")
        foreground = self.__get_style_value("foreground", "#000000")

        self.__canvas.delete("all")
        self.__canvas.configure(width=width, height=height)

        # Draw button itself.
        self.__canvas.create_rectangle(
            0, 0, width, height,
            fill=background,
            outline=""
        )

        # Add progres bar on top.
        if self.__progress is not None:
            self.__canvas.create_rectangle(
                0, 0, width * self.__progress, height,
                fill=adjust_color(background, 0.95),
                outline=""
            )

        # Draw text on top of button.
        self.__canvas.create_text(
            width / 2, height / 2,
            text=self.__text,
            fill=foreground,
            font=self.__font
        )

    def __initialize(self, **kw):
        """
        Used to initialize custom component properties.
        Will only overwrite existing value if it's not None.
        """

        text = safe_get_prop(_TEXT_PROP, **kw)
        progress = safe_get_prop(_PROGRES_PROP, **kw)
        command = safe_get_prop(_COMMAND_PROP, **kw)
        style_name = safe_get_prop(_STYLE_PROP, **kw)
        state = safe_get_prop(_STATE_PROP, **kw)

        if state is not None:
            self.__state = state
            self.__is_disabled = state == "disabled"

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

        width = safe_get_prop(_WIDTH_PROP, **kw)
        height = safe_get_prop(_HEIGHT_PROP, **kw)

        if width is not None:
            self.__width = width

        if self.__width is None:
            self.__width = self.__font.measure(self.__text)

        if height is not None:
            self.__height = height

        if self.__height is None:
            self.__height = 1

        # Remove custom properties before passing kw to parent class.
        props_to_delete = [_STYLE_PROP, _TEXT_PROP, _PROGRES_PROP, _COMMAND_PROP, _STATE_PROP]
        return safe_delete_props(props_to_delete, **kw)

    def __get_style_value(self, prop_name: str, default_value=None):
        """
        Used to get value from style.
        If dynamic property for map configured and state matches configuration
        then dynamic value would be returned.
        """

        if self.__style_name is None:
            return default_value

        default_state_value = style.lookup(self.__style_name, prop_name)

        if default_state_value is None:
            default_state_value = default_value

        if self.__style_name is None or len(self.__style_name) == 0:
            return default_state_value

        for state, value in style.map(self.__style_name, prop_name):
            if state == self.__state:
                return value

        return default_state_value

    def __register_handlers(self):
        """
        Used to register handlers for button events.
        """

        def set_state(state: str):
            """
            Used to register simple events that simply change widget state.
            """

            def handler(_):
                if self.__is_disabled:
                    self.__state = "disabled"
                    return

                self.__state = state
                self.__draw()

            return handler

        def on_release(event):
            """
            Used to register event when button is released.
            Tracks if mouse was released over the button.
            If it was then command would be executed, otherwise it would not.
            """

            if self.__is_disabled:
                self.__state = "disabled"
                return

            width = self.__get_width()
            height = self.__get_height()
            x, y = event.x, event.y

            if 0 <= x <= width and 0 <= y <= height:
                if self.__command is not None:
                    self.__command()

            self.__state = "active"
            self.__draw()

        self.__canvas.unbind("<Button-1>")
        self.__canvas.unbind("<Enter>")
        self.__canvas.unbind("<Leave>")
        self.__canvas.unbind("<ButtonRelease-1>")

        self.__canvas.bind("<Button-1>", set_state("pressed"))
        self.__canvas.bind("<Enter>", set_state("active"))
        self.__canvas.bind("<Leave>", set_state(""))
        self.__canvas.bind("<ButtonRelease-1>", on_release)

    def __init_style(self, style_name: str):
        """
        Used to initialize properties from provided style.
        """

        self.__style_name = style_name
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
