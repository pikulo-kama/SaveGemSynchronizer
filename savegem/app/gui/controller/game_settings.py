from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from savegem.app.gui.component.toggle import QCustomToggle
from savegem.app.gui.controller import WidgetController
from savegem.common.core.context import app
from savegem.common.core.text_resource import tr


class AutoModeController(WidgetController):
    """
    Used to control 'Auto Mode' game setting.
    """

    def setup(self, auto_mode_toggle: QCustomToggle):
        game = app().games.current

        def toggle_auto_mode():
            game.settings.auto_mode = not game.settings.auto_mode

        if game.auto_mode_allowed:
            auto_mode_toggle.clicked.connect(toggle_auto_mode)  # noqa

    def refresh(self, auto_mode_toggle: QCustomToggle):
        game = app().games.current
        is_checked = game.settings.auto_mode
        tooltip = ""

        if not game.auto_mode_allowed:
            is_checked = False
            tooltip = tr("label_SettingIsDisabled")

        auto_mode_toggle.setChecked(is_checked)
        auto_mode_toggle.setToolTip(tooltip)

    def enable(self, auto_mode_toggle: QCustomToggle):
        self.disable(auto_mode_toggle)

    def disable(self, auto_mode_toggle: QCustomToggle):
        if not app().games.current.auto_mode_allowed:
            auto_mode_toggle.setEnabled(False)
