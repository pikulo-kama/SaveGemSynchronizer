from typing import Final
from savegem.app.gui.component import Component
import tkinter as tk
from savegem.app.gui.constants import TkEvent, TkAttr, TkCursor, TkState


# TODO: Without any exaggeration - I hate this file but I'm too lazy to make
#  anything decent from it...
class Dropdown(Component):

    __CHEVRON_SYMBOL: Final = "▼"
    __OPTION_PREFIX: Final = " • "

    def __init__(self, master, **kw):
        self.__dropdown = None
        self.__selected_value = tk.StringVar()
        super().__init__(master, **kw)

    def set(self, value):
        """
        Used to set current dropdown value.
        """

        self.__selected_value.set(value)
        self._draw()

    def _init(self):

        self._set_prop_default_value(TkAttr.Values, [])
        values = self._get_value(TkAttr.Values)

        if len(values) > 0:
            self.__selected_value.set(values[0])

    def _do_draw(self):
        m_left, _, m_right, _ = self._get_margin()

        width = self._get_width()
        height = self._get_height()
        foreground = self._get_value(TkAttr.FgColor)
        prefix = self._get_value(TkAttr.Prefix)
        font = self._get_font()

        text_width = font.measure(prefix) + font.measure(self.__selected_value.get())
        chevron_width = font.measure(self.__CHEVRON_SYMBOL)
        components_width = text_width + chevron_width

        gap = (width - components_width) - m_left - m_right

        self._canvas.create_text(
            m_left + text_width / 2,
            height / 2,
            text=f"{prefix}{self.__selected_value.get()}",
            fill=foreground,
            font=font
        )

        self._canvas.create_text(
            m_left + text_width + gap + chevron_width / 2,
            height / 2,
            text=self.__CHEVRON_SYMBOL,
            fill=foreground,
            font=font
        )

    def _bind_events(self):
        self._canvas.bind(TkEvent.LMBClick, lambda _: self.__toggle_dropdown())

    def _unbind_events(self):
        self._canvas.unbind(TkEvent.LMBClick)

    def __destroy_dropdown(self):
        """
        Used to destroy dropdown.
        """

        self.__dropdown.destroy()
        self.__dropdown = None

    def __toggle_dropdown(self):
        """
        Used to toggle dropdown visibility.
        If dropdown is visible it would be destroyed.
        If vice versa - it would be rendered.
        """

        if self.__dropdown is not None:
            self.__destroy_dropdown()
            return

        values = self._get_value(TkAttr.Values)
        font = self._get_font()

        self.__dropdown = tk.Toplevel(self)
        self.__dropdown.wm_overrideredirect(True)
        self.__dropdown.lift()

        self.__dropdown.configure(background="green", bg="green")
        width = self._get_value(TkAttr.Width)

        background = self._get_value(TkAttr.BgColor)
        foreground = self._get_value(TkAttr.FgColor)

        listbox = _CustomListbox(
            self.__dropdown,
            cursor=TkCursor.Hand,
            width=width,
            values=values,
            command=self.__on_select,
            background=background,
            foreground=foreground,
            prefix=self.__OPTION_PREFIX,
            font=font,
            style=self._get_value(TkAttr.Style) + ".TListbox"
        )

        listbox.pack(fill=tk.X)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()

        # Need to do this to recalculate listbox height.
        self.__dropdown.update_idletasks()
        self.__dropdown.geometry(f"{self._get_width()}x{listbox.height}+{x}+{y}")

    def __on_select(self, value: str):
        """
        Callback that handles option selection.
        """

        command = self._get_value(TkAttr.Command)

        if command is not None:
            command(value)

        self.__selected_value.set(value)
        self.__toggle_dropdown()


class _CustomListbox(Component):
    """
    Represents actual dropdown (list with options).
    Used only internally by Dropdown component.
    """

    def __init__(self, master, **kw):
        self.__hovered_item = None
        self.__options = []
        self.__master = master
        super().__init__(master, **kw)

    def _init(self):
        self.__body = tk.Frame(
            self.__master,
            borderwidth=0,
            highlightthickness=0
        )

        self.__body.pack(side=tk.TOP, fill=tk.X, expand=True)
        self._set_prop_default_value(TkAttr.Prefix, "")

    @property
    def height(self):
        return self.__body.winfo_height()

    def _draw(self):
        original_state = self._get_value(TkAttr.State)
        prefix = self._get_value(TkAttr.Prefix)
        values = self._get_value(TkAttr.Values)

        for idx, value in enumerate(values):
            label = self.__options[idx]

            # We dynamically change state per option
            # to be able to retrieve colors from dynamic map.
            if self.__hovered_item == value:
                self._set_value(TkAttr.State, TkState.Active)
            else:
                self._set_value(TkAttr.State, TkState.Default)

            background = self._get_value(TkAttr.BgColor)
            foreground = self._get_value(TkAttr.FgColor)

            label.configure(
                bg=background,
                fg=foreground,
                text=prefix + value
            )

        # Restore state
        self._set_value(TkAttr.State, original_state)

    def _post_init(self):
        values = self._get_value(TkAttr.Values)
        font = self._get_font()

        self.__clear()

        for _ in values:
            label = tk.Label(
                self.__body,
                anchor=tk.NW,
                pady=5,
                cursor=TkCursor.Hand,
                font=font
            )

            label.pack(fill=tk.X, expand=True)
            self.__options.append(label)

    def _bind_events(self):

        values = self._get_value(TkAttr.Values)
        for idx, option in enumerate(self.__options):
            value = values[idx]

            option.bind(TkEvent.LMBClick, self.__on_select)
            option.bind(TkEvent.Enter, self.__set_state_and_selection(value, TkState.Active))
            option.bind(TkEvent.Leave, self.__set_state_and_selection(value, TkState.Default))

    def _unbind_events(self):

        for option in self.__options:
            option.unbind(TkEvent.LMBClick)
            option.unbind(TkEvent.Enter)
            option.unbind(TkEvent.Leave)

    def __clear(self):
        """Clear all items"""
        for item in self.__options:
            item.destroy()

        self.__options.clear()

    def __on_select(self, event):
        """
        Callback that handles option selection.
        """

        command = self._get_value(TkAttr.Command)

        if command is not None:
            value = event.widget.cget("text")
            prefix = self._get_value(TkAttr.Prefix)
            value = value.replace(prefix, "")

            command(value)

    def __set_state_and_selection(self, selection, state):
        """
        Callback used to change state
        and store name of hovered option.
        """

        def handler(_):
            if state == TkState.Active:
                self.__hovered_item = selection
            else:
                self.__hovered_item = None

            state_callback = self._set_state_handler(state)
            state_callback(_)

        return handler
