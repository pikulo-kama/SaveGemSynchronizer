from src.gui.constants import TkState, TkEvent
from src.gui.component import Component, TkAttr
import tkinter as tk

from src.util.graphics import create_polygon


class Button(Component):

    def _init(self):
        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._set_prop_default_value(TkAttr.Text, "")
        self._set_prop_default_value(TkAttr.Radius, 0)
        self._set_prop_default_value(TkAttr.BgColor, "#ffffff")
        self._set_prop_default_value(TkAttr.FgColor, "#000000")

    def _do_draw(self):
        width = self._get_width()
        height = self._get_height()

        text = self._get_value(TkAttr.Text)
        radius = self._get_value(TkAttr.Radius)
        background = self._get_value(TkAttr.BgColor)
        foreground = self._get_value(TkAttr.FgColor)

        self._canvas.delete("all")
        self._canvas.configure(width=width, height=height)

        # Draw button body.
        create_polygon(
            0, 0, width, height,
            widget=self._canvas,
            radius=radius,
            fill=background,
            outline=""
        )

        self._draw_on_body()

        # Draw text on top of button.
        self._canvas.create_text(
            width / 2, height / 2,
            text=text,
            fill=foreground,
            font=self._get_font()
        )

    def _draw_on_body(self):
        """
        Should be used to draw additional elements
        over button main canvas.
        """
        pass

    def _bind_events(self):
        # Buttons should be non interactable when they are disabled.
        if self._get_value(TkAttr.State) == TkState.Disabled:
            return

        self._canvas.bind(TkEvent.LMBClick, self.__set_state(TkState.Pressed))
        self._canvas.bind(TkEvent.Enter, self.__set_state(TkState.Active))
        self._canvas.bind(TkEvent.Leave, self.__set_state(TkState.Default))
        self._canvas.bind(TkEvent.LMBRelease, lambda e: self.__on_release(e))

    def _unbind_events(self):
        self._canvas.unbind(TkEvent.LMBClick)
        self._canvas.unbind(TkEvent.Enter)
        self._canvas.unbind(TkEvent.Leave)
        self._canvas.unbind(TkEvent.LMBRelease)

    def __set_state(self, state: str):
        """
        Used to register simple events that simply change widget state.
        """

        def handler(_):
            self._set_value(TkAttr.State, state)
            self._draw()

        return handler

    def __on_release(self, event):
        """
        Used to register event when button is released.
        Tracks if mouse was released over the button.
        If it was then command would be executed, otherwise it would not.
        """

        width = self._get_width()
        height = self._get_height()
        command = self._get_value(TkAttr.Command)
        x, y = event.x, event.y

        # Check if button was released while cursor was in bound of button.
        if command is not None and 0 <= x <= width and 0 <= y <= height:
            command()

        self._draw()
