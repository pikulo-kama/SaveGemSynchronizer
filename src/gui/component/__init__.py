import tkinter as tk
from tkinter import font
from tkinter.font import Font

from src.gui.constants import TkAttr, TkState
from src.gui.style import style
from src.util.graphics import create_polygon


class Component(tk.Frame):
    """
    Wrapper for Tkinter frame.
    Should be used as base for all custom components.
    """

    __DEFAULT_FONT_NAME = "TkDefaultFont"

    def __init__(self, master, **kw):

        self.__prop_default_values = {}
        self.__previous_props = kw
        self.__props = kw
        self.__is_destroying = False

        self._pre_init()
        kw = self.__delete_custom_props(tk.Frame(master), **kw)
        super().__init__(master, **kw)

        self._canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief=tk.FLAT)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self.__register_default_values()
        self._init()
        self.__sync_props()
        self._post_init()

        if self._get_value(TkAttr.State) != TkState.Disabled:
            self._bind_events()

        self._draw()

    def configure(self, cnf=None, **kw):
        self._unbind_events()
        self.__props = kw

        self._pre_init()
        kw = self.__delete_custom_props(self, **kw)
        super().configure(cnf, **kw)
        self.__sync_props()
        self._post_init()

        if self._get_value(TkAttr.State) != TkState.Disabled:
            self._bind_events()

        self._draw()

    def destroy(self):
        self.__is_destroying = True

        self._unbind_events()
        super().destroy()

    def _draw(self):
        """
        Guarded version of _do_draw.
        Should always be used to render inside event handlers.
        """

        if self.__is_destroying:
            return

        width = self._get_width()
        height = self._get_height()
        radius = self._get_value(TkAttr.Radius)
        background = self._get_value(TkAttr.BgColor)

        self._canvas.delete(tk.ALL)
        self._canvas.configure(width=width, height=height)

        # Draw component body.
        create_polygon(
            0, 0, width, height,
            widget=self._canvas,
            radius=radius,
            fill=background,
            outline=""
        )

        self._do_draw()

    def _init(self):
        """
        Should be to initialize component custom state as well as define
        default values for custom properties.
        """
        pass

    def _pre_init(self):
        """
        This function is executed before Frame is being created
        and before configure is called. Use it when you want to intercept some
        of the values and make some changes to them.
        """
        pass

    def _post_init(self):
        """
        This function is executed after Frame is created and
        after all properties have been synchronized.
        """
        pass

    def _do_draw(self):
        """
        To be implemented in child classes.
        Should be used to draw/render actual component.
        """
        pass

    def _bind_events(self):
        """
        Should be used to bind component events with handlers.
        Called each time component is created or updated.
        """
        pass

    def _unbind_events(self):
        """
        Should be used to unbind component events.
        Doesn't get called on creation only when component is updated.
        """
        pass

    def _set_state_handler(self, state: str):
        """
        Used to register simple events that simply change widget state.
        """

        def handler(_):
            self._set_value(TkAttr.State, state)
            self._draw()

        return handler

    def _get_value(self, prop_name: str):
        """
        Used to get widget property.
        The following places are being queried in
        the following order:

        - Value from current state (will take from prev if current is None)
        - If style is not None will query dynamic map data
        - If dynamic map data was not found for prop + state - take value from style config.
        - Will return style value if not None or else widget level value
        """

        def get_prop(name: str):
            value = self.__props.get(name)
            previous_value = self.__previous_props.get(name)

            return value if value is not None else previous_value

        # Style and state are special attributes since they impact
        # retrieval of other properties, if any of those miss need to
        # check if they were provided initially.
        style_name = get_prop(TkAttr.Style)
        component_state = get_prop(TkAttr.State)
        widget_value = get_prop(prop_name)
        default_value = self.__prop_default_values.get(prop_name)

        # If there is no style then use widget level value.
        if style_name is None or len(style_name) == 0:
            return widget_value

        # If there is dynamic value configured for current state - then use it.
        for state, dynamic_value in style.map(style_name, prop_name):
            if state == component_state:
                return dynamic_value

        # Value defined on widget level has higher priority than value in style.
        if widget_value is not None and widget_value != default_value:
            return widget_value

        # If no dynamic data for property and widget value is None
        # then get value defined on style.
        style_body = dict(style.configure(style_name))
        style_value = style_body.get(prop_name)

        return style_value if style_value is not None else default_value

    def _set_value(self, prop_name: str, prop_value):
        """
        Used to set property value in current state.
        """
        self.__props[prop_name] = prop_value

    def _set_prop_default_value(self, prop_name: str, default_value):
        """
        Should be used to add default value for property.
        """
        self.__prop_default_values[prop_name] = default_value

    def _get_width(self):
        """
        Used to get true width of button.
        Takes into consideration paddings.
        """

        p_left, _, p_right, _ = self._get_padding()
        char_width: int = self._get_value(TkAttr.Width)
        text: str = self._get_value(TkAttr.Text)

        font_obj = self._get_font()
        width = font_obj.measure(text)

        if char_width is not None:
            width = font_obj.measure("0") * char_width

        return width + p_left + p_right

    def _get_height(self):
        """
        Used to get true height of button.
        Takes into consideration paddings.
        """

        _, p_top, _, p_bottom = self._get_padding()
        height: int = self._get_value(TkAttr.Height)
        font_obj = self._get_font()

        return height * font_obj.metrics("linespace") + p_top + p_bottom

    def _get_font(self):
        """
        Should be used to get current font.
        """

        font_obj = self._get_value(TkAttr.Font)

        if font_obj is None:
            return None

        if isinstance(font_obj, Font):
            return font_obj

        return font.Font(root=None, font=self.__parse_font(font_obj))

    def __sync_props(self):
        """
        Used to synchronize component properties.
        To collect all keys that are being used the following
        places are being queried: current props, props before last update
        and default props which are defined per component.

        New value for the property is being queried from different sources
        once value is found it would be used as current value.

        Places that are being queried in their querying order:
        - Properties from current state
        - Properties from previous state
        - Default values from properties

        If value was found in one of the places it would be used to
        populate current property value as well as value from previous state.
        """

        previous_keys = list(self.__previous_props.keys())
        provided_keys = list(self.__props.keys())
        keys_with_defaults = list(self.__prop_default_values.keys())

        keys = list(set(previous_keys + provided_keys + keys_with_defaults))

        # Update properties. If property is not provided on update, but it
        # was provided during initialization then initial value would be used.
        # If initial value is missing as well, then default value would be used.
        for name in keys:
            value = self.__props.get(name)

            # First try from previous props.
            if value is None:
                value = self.__previous_props.get(name)

            # Lastly check for default value for property.
            if value is None:
                value = self.__prop_default_values.get(name)

            if value is not None:
                self.__previous_props[name] = value

            self.__props[name] = value

    def __register_default_values(self):
        """
        Internal method.
        Used to register default values for on root level.
        """

        self._set_prop_default_value(TkAttr.State, TkState.Default)
        self._set_prop_default_value(TkAttr.Font, font.nametofont(self.__DEFAULT_FONT_NAME))
        self._set_prop_default_value(TkAttr.Height, 1)
        self._set_prop_default_value(TkAttr.Text, "")
        self._set_prop_default_value(TkAttr.Radius, 0)
        self._set_prop_default_value(TkAttr.BgColor, "#ffffff")
        self._set_prop_default_value(TkAttr.FgColor, "#000000")
        self._set_prop_default_value(TkAttr.Padding, (0, 0, 0, 0))
        self._set_prop_default_value(TkAttr.Margin, (0, 0, 0, 0))

    def _get_padding(self):
        """
        Used to get padding tuple.
        """
        return self.__obj_to_tuple(self._get_value(TkAttr.Padding))

    def _get_margin(self):
        """
        Used to get margin tuple.
        """
        return self.__obj_to_tuple(self._get_value(TkAttr.Margin))

    @staticmethod
    def __obj_to_tuple(obj):
        """
        Used to unwrap padding/margin
        object into tuple of 4 values.
        """

        # Handle string padding.
        if isinstance(obj, str):
            obj = tuple(int(value) for value in obj.split(" "))

        # Handle single value.
        if isinstance(obj, int):
            return obj, obj, obj, obj

        if len(obj) == 2:
            return obj[0], obj[1], obj[0], obj[1]

        elif len(obj) == 4:
            return obj

        else:
            raise ValueError("Expected 1, 2, or 4 values")

    @staticmethod
    def __parse_font(font_obj: str):
        """
        Used to parse font object and format it,
        returning either style name, style name + font_size
        or style_name + font_size + boldness.
        """

        # No need to do anything if it's already tuple.
        if isinstance(font_obj, tuple):
            return font_obj

        # If font is configured just as a number.
        if isinstance(font_obj, int):
            return Component.__DEFAULT_FONT_NAME, font_obj

        font_name_start = font_obj.index("{")
        font_name_end = font_obj.index("}")

        font_name = font_obj[font_name_start + 1:font_name_end]
        font_parts = str(font_obj[font_name_end + 1:]).strip().split(" ")

        if len(font_parts) == 1:
            return font_name, int(font_parts[0])

        if len(font_parts) > 1:
            return font_name, int(font_parts[0]), font_parts[1]

        return font_name

    @staticmethod
    def __delete_custom_props(widget, **kw):
        """
        Should be used to delete all properties
        from component which are custom.
        """

        for prop_name in list(kw.keys()):
            if prop_name not in widget.keys():
                del kw[prop_name]

        return kw
