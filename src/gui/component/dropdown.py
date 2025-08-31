from typing import Final
from src.gui.component import Component
import tkinter as tk
from src.gui.constants import TkEvent, TkAttr, TkCursor


# TODO: Without any exaggeration - I hate this file but I'm too lazy to make
#  anything decent from it...
class Dropdown(Component):

    __CHEVRON_SYMBOL: Final = "▼"
    __OPTION_PREFIX: Final = " • "
    __OPTION_SEPARATOR: Final = "━"

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

        self._set_prop_default_value(TkAttr.Values, [None])

        values = self._get_value(TkAttr.Values)
        self.__selected_value.set(values[0])

    def _do_draw(self):
        m_left, _, m_right, _ = self._get_margin()

        width = self._get_width()
        height = self._get_height()
        foreground = self._get_value(TkAttr.FgColor)
        prefix = self._get_value(TkAttr.Prefix)
        font = self._get_font()

        text_width = font.measure(self.__selected_value.get()) + font.measure(prefix)
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

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self._get_width()

        # +1 For extra empty first line to create visual separation between options and main component.
        height = font.metrics("linespace") * (len(values) * 2 + 1)

        # +1 just in case there would be gap from separator.
        char_width = int(width / font.measure(self.__OPTION_SEPARATOR)) + 1

        self.__dropdown.geometry(f"{width}x{height}+{x}+{y}")

        background = self._get_value(TkAttr.BgColor)
        foreground = self._get_value(TkAttr.FgColor)

        listbox = tk.Listbox(
            self.__dropdown,
            bg=background,
            fg=foreground,
            relief=tk.FLAT,
            cursor=TkCursor.Hand,
            font=font
        )

        for idx, value in enumerate(values):
            separator = ""

            if idx > 0:
                separator = self.__OPTION_SEPARATOR * char_width

            listbox.insert(tk.END, separator)
            listbox.insert(tk.END, f"{self.__OPTION_PREFIX}{value}")

        listbox.pack(fill=tk.BOTH, expand=True)
        listbox.bind(TkEvent.ListboxSelected, self.__on_select)

    def __on_select(self, event):
        """
        Callback that handles option selection.
        """

        widget = event.widget
        command = self._get_value(TkAttr.Command)

        selection = widget.get(widget.curselection())
        selection = str(selection).replace(self.__OPTION_PREFIX, "")

        if command is not None:
            command(event, selection)

        self.__selected_value.set(selection)
        self.__toggle_dropdown()
