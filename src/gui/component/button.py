from src.gui.constants import TkState, TkEvent
from src.gui.component import Component, TkAttr


class Button(Component):
    """
    Custom Tkinter button component.
    """

    def _do_draw(self):
        width = self._get_width()
        height = self._get_height()
        text = self._get_value(TkAttr.Text)
        foreground = self._get_value(TkAttr.FgColor)

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
        self._canvas.bind(TkEvent.LMBClick, self._set_state_handler(TkState.Pressed))
        self._canvas.bind(TkEvent.Enter, self._set_state_handler(TkState.Active))
        self._canvas.bind(TkEvent.Leave, self._set_state_handler(TkState.Default))
        self._canvas.bind(TkEvent.LMBRelease, lambda e: self.__on_release(e))

    def _unbind_events(self):
        self._canvas.unbind(TkEvent.LMBClick)
        self._canvas.unbind(TkEvent.Enter)
        self._canvas.unbind(TkEvent.Leave)
        self._canvas.unbind(TkEvent.LMBRelease)

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
