from constants import File
from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.window import gui
from savegem.common.core.text_resource import tr
from savegem.common.util.file import delete_file, resolve_app_data


class LogoutController(WidgetController):
    """
    Used to control logout button.
    """

    def setup(self, logout_button: QCustomPushButton):
        logout_button.clicked.connect(  # noqa
            lambda: gui().confirmation(
                tr("confirmation_ConfirmLogout"),
                self.__logout
            )
        )

    def __logout(self):
        """
        Logout callback.
        Used to perform user cleanup action and destroy main window.
        """

        # Delete auth token.
        delete_file(resolve_app_data(File.GDriveToken))
        self.manager.gui.destroy()
