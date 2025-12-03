import pytest
from PyQt6.QtCore import Qt
from unittest.mock import call
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestPlayersController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, _player_a, _player_b, _player_c, _player_d, user_config_mock, games_config_mock,
               _active_players, _widget_mock, _label_mock, _spacer_mock, _h_layout_mock, resolve_content_mock):
        """
        Provides mock user/player data configured for sorting and filtering tests.
        """

        all_users = [_player_a, _player_b, _player_c, _player_d]
        user_config_mock.__iter__.return_value = all_users
        games_config_mock.current.players = [_player_a.email, _player_b.email, _player_c.email]

    @pytest.fixture
    def _active_players(self, _player_a, _player_b, activity_mock):
        players = [_player_a, _player_b]
        activity_mock.players = players

        return players

    @pytest.fixture
    def _players_container(self, mocker: MockerFixture):
        """
        Mocks the QCustomWidget instance for players.
        """
        return mocker.MagicMock()

    @pytest.fixture
    def _player_a(self, mocker: MockerFixture):
        return self._create_player_mock(mocker, "Amy Adams", "amy@a.com", "amy.png")

    @pytest.fixture
    def _player_b(self, mocker: MockerFixture):
        return self._create_player_mock(mocker, "Bob Brown", "bob@b.com", "bob.png")

    @pytest.fixture
    def _player_c(self, mocker: MockerFixture):
        return self._create_player_mock(mocker, "Carl Johnson", "carl@c.com", "carl.png")

    @pytest.fixture
    def _player_d(self, mocker: MockerFixture):
        return self._create_player_mock(mocker, "Zoe Smith", "zoe@a.com", "zoe.png")

    @staticmethod
    def _create_player_mock(mocker: MockerFixture, name: str, email: str, photo: str):
        player = mocker.MagicMock()
        player.name = name
        player.short_name = name.split()[0]
        player.email = email
        player.photo = photo

        return player

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the PlayersController instance.
        """

        from savegem.app.gui.controller.players import PlayersController
        return PlayersController(_widget_manager)

    def test_refresh_renders_and_sorts_players(self, _controller, _widget_manager, _players_container, _player_a,
                                               _player_b, _player_c, _widget_mock, _label_mock,
                                               _active_players, resolve_content_mock):
        """
        Tests that refresh filters users by game access, sorts correctly (active first, then name),
        and sets the 'active' property.
        """

        from savegem.app.gui.constants import QAttr

        _controller.refresh(_players_container)

        # 1. Assert cleanup
        _widget_manager.remove_child_widgets.assert_called_once_with(_players_container)

        # 2. Verify expected order (Active first, then alphabetical by name):
        # Users rendered: Amy (Active), Bob (Active), Carl (Inactive)
        # Zoe (Non-game user) is filtered out.

        expected_users = [
            _player_a,  # Amy Adams (Active, A)
            _player_b,  # Bob Brown (Active, B)
            _player_c,  # Carl Johnson (Inactive, C)
        ]

        # Check calls on the mock layout adder (3 players * 2 widgets + 1 spacer)
        add_widget_mock = _players_container.layout.return_value.add_dynamic_widget
        assert add_widget_mock.call_count == 3

        for i, user in enumerate(expected_users):
            is_active = user in _active_players

            # Since QCustomWidget is instantiated 3 times, we need the Nth call
            player_card_mock = _widget_mock.call_args_list[i].return_value

            # Active Check: property must be set if active
            if is_active:
                player_card_mock.setProperty.assert_any_call(QAttr.Id, "active")
            else:
                # Ensure the 'active' property is NOT set on the inactive user (Carl)
                assert call(QAttr.Id, "active") not in player_card_mock.setProperty.call_args_list

            # Profile picture set with resolved content (using the user's photo string)
            expected_pixmap_content = f"RESOLVED(pixmap{{{user.photo}, scale: 30, circle}})"

            # QCustomLabel is mocked, so we just check that the correct content was *passed*
            # The profile picture label is the (i*2)th label instance created:
            profile_pic_mock = _label_mock.call_args_list[i * 2].return_value
            profile_pic_mock.setPixmap.assert_called_once_with(expected_pixmap_content)

            # Username label setup (the (i*2 + 1)th label instance created)
            user_name_mock = _label_mock.call_args_list[i * 2 + 1].return_value
            user_name_mock.setText.assert_called_once_with(user.short_name)
            user_name_mock.setAlignment.assert_called_once_with(Qt.AlignmentFlag.AlignTop)

    def test_refresh_handles_no_game_players(self, _controller, _players_container, _widget_mock, games_config_mock):
        """
        Tests the case where app().games.current.players is empty (meaning all players are relevant).
        """

        # FIX: Set game players list to empty list (this implies no filtering by game access)
        games_config_mock.current.players = []
        _controller.refresh(_players_container)

        # Since the game player list is empty, NO filtering should occur based on game access.
        # All 4 users (Amy, Bob, Carl, Zoe) should be rendered.

        # Assert 4 player cards were created (4 players total)
        assert _widget_mock.call_count == 4
