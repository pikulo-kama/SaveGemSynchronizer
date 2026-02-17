import os
import subprocess

from PyQt6.QtWidgets import QFileDialog
from kui.component.button import KamaPushButton
from kui.component.toggle import KamaToggle
from kui.core.app import KamaApplication
from kui.core.controller import WidgetController
from kui.core.metadata import ControllerArgs
from kui.core.shortcut import tr
from kutil.logger import get_logger

from savegem.common.core.context import context


_logger = get_logger(__name__)


class AutoModeController(WidgetController):
    """
    Used to control 'Auto Mode' game setting.
    """

    def setup(self, auto_mode_toggle: KamaToggle, args: ControllerArgs):

        def toggle_auto_mode():
            game = context().games.current

            _logger.info("Setting 'Auto Mode' for %s to %s", game.name, not game.settings.auto_mode)
            game.settings.auto_mode = not game.settings.auto_mode

        if not context().games.current.auto_mode_allowed:
            _logger.warning("'Auto Mode' is not allowed for %s. Click bind won't be applied.", context().games.current.name)
            return

        auto_mode_toggle.clicked.connect(toggle_auto_mode)  # noqa

    def refresh(self, auto_mode_toggle: KamaToggle, args: ControllerArgs):
        game = context().games.current
        is_checked = game.settings.auto_mode
        tooltip = ""

        if not game.auto_mode_allowed:
            _logger.warning("'Auto Mode' is not allowed for %s. Disabling setting.", game.name)

            is_checked = False
            tooltip = tr("label_SettingIsDisabled")

        auto_mode_toggle.setChecked(is_checked)
        auto_mode_toggle.setToolTip(tooltip)

    def enable(self, auto_mode_toggle: KamaToggle, args: ControllerArgs):
        self.disable(auto_mode_toggle, args)

    def disable(self, auto_mode_toggle: KamaToggle, args: ControllerArgs):
        if not context().games.current.auto_mode_allowed:
            auto_mode_toggle.setEnabled(False)


class OpenSaveLocationButtonController(WidgetController):

    def setup(self, open_button: KamaPushButton, args: ControllerArgs):
        open_button.clicked.connect(
            lambda: subprocess.run(["explorer", os.path.normpath(context().games.current.local_path)])
        )


class ChangeStoragePathButtonController(WidgetController):

    def setup(self, modify_button: KamaPushButton, args: ControllerArgs):

        def change_path():
            current_game = context().games.current
            existing_path = current_game.local_path
            new_path = QFileDialog.getExistingDirectory(
                KamaApplication().window,
                tr("label_SelectTargetDirectory"),
                existing_path,
                QFileDialog.Option.ShowDirsOnly
            )

            if new_path == existing_path or len(new_path) == 0:
                return

            current_game.settings.local_storage_path = new_path
            current_game.meta.local.calculate_checksum()
            self.manager.event_refresh("local_storage_path_change")

        modify_button.clicked.connect(change_path)
