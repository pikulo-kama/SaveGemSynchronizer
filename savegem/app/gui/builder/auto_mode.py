from savegem.app.gui.component.button import Button
from savegem.app.gui.style import style
from savegem.app.gui.popup.notification import notification
from savegem.common.core import app
from savegem.common.core.holders import prop
from savegem.app.gui.window import _GUI
from savegem.app.gui.constants import TkState, TkCursor, TkAttr
from savegem.app.gui.builder import UIBuilder
from savegem.common.core.text_resource import tr
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class AutoModeBuilder(UIBuilder):
    """
    Used to build button to enable auto download/upload mode.
    Always enabled.
    """

    def __init__(self):
        super().__init__()
        self.__style_name = "SquareSecondary.18.TButton"
        self.__auto_mode_button = None

    def build(self, gui: _GUI):
        self.__add_auto_mode_button(gui)

    def refresh(self, gui: _GUI):

        if app.state.is_auto_mode:
            style_props = style.configure(self.__style_name)
            background = style_props.get(TkAttr.BgColor)
            foreground = style_props.get(TkAttr.FgColor)

        else:
            background = prop("secondaryColor")
            foreground = prop("primaryButton.colorHover")

        self.__auto_mode_button.configure(
            text="A",
            background=background,
            foreground=foreground
        )

        _logger.debug(
            "Auto mode updated, current state = %s",
            "ON" if app.state.is_auto_mode else "OFF"
        )

    def enable(self, gui: "_GUI"):
        self.__auto_mode_button.configure(state=TkState.Default, cursor=TkCursor.Hand)

    def disable(self, gui: "_GUI"):
        self.__auto_mode_button.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_auto_mode_button(self, gui: _GUI):
        """
        Used to render auto upload/download button.
        """

        def callback():
            # Toggle state of button
            if app.state.is_auto_mode:
                app.state.is_auto_mode = False
                message = tr("notification_AutoModeOff")

            else:
                app.state.is_auto_mode = True
                message = tr("notification_AutoModeOn")

            # No need to fully reload the UI since no other visual components
            # would be affected.
            self.refresh(gui)
            notification(message)

        self.__auto_mode_button = Button(
            gui.top_left,
            command=callback,
            style=self.__style_name
        )

        self.__auto_mode_button.grid(row=0, column=0, padx=(20, 0), pady=(20, 0))
