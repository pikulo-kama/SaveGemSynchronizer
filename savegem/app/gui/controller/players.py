from PyQt6.QtCore import Qt

from savegem.app.gui.component.label import QCustomLabel
from savegem.app.gui.component.layout import QCustomLayout, QCustomHBoxLayout
from savegem.app.gui.component.spacer import QSpacer
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import QAttr
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.widget.resolver import resolve_content
from savegem.common.core.context import app


class PlayersController(WidgetController):

    def refresh(self, players_container: QCustomWidget):

        players_layout: QCustomLayout = players_container.layout()
        self.manager.remove_child_widgets(players_container)

        # Sort by name but make sure to show players that are online first.
        user_list = sorted(app().users, key=lambda u: (u not in app().activity.players, u.name))
        game_players = app().games.current.players

        for user in user_list:

            # Only show players that are relevant to the current game.
            if len(game_players) > 0 and user.email not in game_players:
                continue

            player_card = QCustomWidget()
            player_card_layout = QCustomHBoxLayout(player_card)
            profile_picture_label = QCustomLabel()
            user_name_label = QCustomLabel()

            if user in app().activity.players:
                player_card.setProperty(QAttr.Id, "active")

            profile_picture = resolve_content("pixmap{" + user.photo + ", scale: 30, circle}")
            profile_picture_label.setPixmap(profile_picture)
            user_name_label.setText(user.short_name)
            user_name_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            user_name_label.setContentsMargins(5, 5, 0, 0)

            players_layout.add_dynamic_widget(player_card)

            player_card_layout.add_dynamic_widget(profile_picture_label)
            player_card_layout.add_dynamic_widget(user_name_label)
            player_card_layout.add_dynamic_widget(QSpacer())
