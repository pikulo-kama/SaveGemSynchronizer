import tkinter as tk

from src.core.AppState import AppState
from src.core.holders import prop, game_prop
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from src.service.UserService import UserService
from src.util.logger import get_logger

logger = get_logger(__name__)


class XboxUserListVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_active_users_section(gui.window)

    def is_enabled(self):
        return prop("xboxPluginEnabled") is True

    def refresh(self, gui: GUI):
        pass

    @staticmethod
    def __add_active_users_section(gui):

        if game_prop("xboxPresence") is None:
            # Even if XBOX plugin is enabled, we need to additionally check if
            # presence is configured per game.
            # It's impossible to determine state of users without presence
            logger.warn("Can't add XBOX controls for game called %s", AppState.get_game())
            logger.warn("Reason: Missing XBOX presence configured.")
            return

        user_data = UserService().get_user_data()
        # Show online users first.
        user_data.sort(key=lambda u: u["isPlaying"], reverse=True)

        vertical_frame = tk.Frame(gui.window, pady=5)

        for idx, user in enumerate(user_data):

            user_frame = tk.Frame(vertical_frame)

            active_user_config = prop("xboxUserActive")
            inactive_user_config = prop("xboxUserInactive")

            def get_user_prop(property_name: str) -> str:
                if user["isPlaying"]:
                    return active_user_config[property_name]
                else:
                    return inactive_user_config[property_name]

            user_name_label = tk.Label(
                user_frame,
                fg=get_user_prop("fg"),
                text=user["name"],
                justify="left",
                anchor="w",
                font=('Minion Pro SmBd', 10)
            )

            is_playing_label = tk.Label(
                user_frame,
                text="⚫",
                fg=get_user_prop("bg"),
                justify="left",
                anchor="w"
            )

            is_playing_label.grid(row=0, column=0)
            user_name_label.grid(row=0, column=1)

            user_frame.grid(row=idx, column=0, sticky=tk.W)

        vertical_frame.place(rely=.95, relx=.05, anchor=tk.SW)
