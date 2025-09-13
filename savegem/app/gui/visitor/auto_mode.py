from savegem.common.core import app
from savegem.common.core.holders import prop
from savegem.app.gui import _GUI, TkCursor
from savegem.app.gui.component.wait_button import WaitButton
from savegem.app.gui.constants import TkState
from savegem.app.gui.visitor import Visitor
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class AutoModeVisitor(Visitor):
    """
    Used to build button to enable auto download/upload mode.
    Always enabled.
    """

    def __init__(self):
        self.__auto_mode_button = None

    def visit(self, gui: _GUI):
        self.__add_auto_mode_button(gui)

    def refresh(self, gui: _GUI):

        background = "secondaryColor"
        foreground = "primaryButton.colorHover"

        if app.state.is_auto_mode:
            background = "primaryButton.colorStatic"
            foreground = "primaryColor"

        self.__auto_mode_button.configure(
            text="A",
            background=prop(background),
            foreground=prop(foreground),
            state=TkState.Default,
            cursor=TkCursor.Hand
        )
        # _logger.debug("Copyright was reloaded. (%s)", )

    def disable(self, gui: "_GUI"):
        self.__auto_mode_button.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_auto_mode_button(self, gui: _GUI):
        """
        Used to render auto upload/download button.
        """

        def callback():
            # Toggle state of button
            app.state.is_auto_mode = not app.state.is_auto_mode
            # No need to fully reload the UI since nothing will mostly change.
            self.refresh(gui)
            # notification("Auto Mode was enabled.")

        self.__auto_mode_button = WaitButton(
            gui.top_left,
            command=callback,
            style="SquareSecondary.18.TButton"
        )

        self.__auto_mode_button.grid(row=0, column=1, padx=(10, 0), pady=(20, 0))
