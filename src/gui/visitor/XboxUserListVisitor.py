import tkinter as tk

from constants import ACTIVE_USER_STATE_LABEL
from src.core.holders import prop
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from src.service.user_service import UserService


class XboxUserListVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_active_users_section(gui.window)

    def is_enabled(self):
        return prop("xboxPluginEnabled") is True

    @staticmethod
    def __add_active_users_section(gui):

        user_data = UserService().get_user_data()
        user_data.sort(key=lambda u: u["isPlaying"], reverse=True)

        vertical_frame = tk.Frame(gui.window, pady=5)

        for idx, user in enumerate(user_data):

            user_frame = tk.Frame(vertical_frame)
            is_playing = user["isPlaying"]

            active_user_config = prop("xboxUserActive")
            inactive_user_config = prop("xboxUserInactive")

            user_label = tk.Label(
                user_frame,
                fg=active_user_config["fg"] if is_playing else inactive_user_config["fg"],
                text=user["name"],
                justify="left",
                anchor="w",
                font=('Minion Pro SmBd', 10)
            )
            user_state_label = tk.Label(
                user_frame,
                text=ACTIVE_USER_STATE_LABEL,
                fg=active_user_config["bg"] if is_playing else inactive_user_config["bg"],
                justify="left",
                anchor="w"
            )

            user_state_label.grid(row=0, column=0)
            user_label.grid(row=0, column=1)

            user_frame.grid(row=idx, column=0, sticky=tk.W)

        vertical_frame.place(rely=.95, relx=.05, anchor=tk.SW)
