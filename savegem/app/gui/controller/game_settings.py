from savegem.app.gui.component.toggle import QCustomToggle
from savegem.app.gui.controller import WidgetController
from savegem.common.core.context import app


class AutoModeController(WidgetController):
    """
    Used to control 'Auto Mode' game setting.
    """

    def setup(self, auto_mode_toggle: QCustomToggle):

        def toggle_auto_mode():
            game_settings = app().games.current.settings
            game_settings.auto_mode = not game_settings.auto_mode

        auto_mode_toggle.clicked.connect(toggle_auto_mode)  # noqa

    def refresh(self, auto_mode_toggle: QCustomToggle):
        auto_mode_toggle.setChecked(app().games.current.settings.auto_mode)
