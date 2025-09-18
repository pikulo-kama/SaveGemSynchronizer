from constants import File
from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.window import _GUI
from savegem.app.gui.constants import TkCursor
import tkinter as tk

from savegem.app.gui.component.button import Button
from savegem.app.gui.component.chip import Chip
from savegem.app.gui.constants import TkState
from savegem.app.gui.popup.confirmation import confirmation
from savegem.common.util.file import delete_file, resolve_app_data


class UserSectionBuilder(UIBuilder):
    """
    Used to render user section.
    Contains user chip with name and picture
    as well as logout button.
    """

    def __init__(self):
        super().__init__()
        self.__logout_button = None

    def build(self, gui: "_GUI"):
        self.__add_user_section(gui)

    def refresh(self, gui: "_GUI"):
        pass

    def enable(self, gui: "_GUI"):
        self.__logout_button.configure(state=TkState.Default, cursor=TkCursor.Hand)

    def disable(self, gui: "_GUI"):
        self.__logout_button.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_user_section(self, gui: "_GUI"):
        """
        Used to render user section.
        """

        user_section = tk.Frame(gui.top_right)

        user_chip = Chip(
            user_section,
            text=app.user.short_name,
            image=app.user.photo,
            margin=(10, 0),
            width=20,
            style="Primary.TChip"
        )

        self.__logout_button = Button(
            user_section,
            text="➠]",
            command=lambda: confirmation(
                tr("confirmation_ConfirmLogout"),
                lambda: self.__logout(gui)
            ),
            height=2,
            padding=(8, 4),
            style="SquareSecondary.10.TButton",
        )

        user_chip.grid(row=0, column=0, padx=(0, 10))
        self.__logout_button.grid(row=0, column=1)

        user_section.grid(row=0, column=0, sticky=tk.E, padx=(0, 20), pady=(20, 0))

    @staticmethod
    def __logout(gui: "_GUI"):
        """
        Logout callback.
        Used to perform user cleanup action and destroy main window.
        """

        # Delete auth token.
        delete_file(resolve_app_data(File.GDriveToken))
        gui.destroy()
