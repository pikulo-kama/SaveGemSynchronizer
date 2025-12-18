import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestPlayersController(WidgetControllerTest):

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the PlayersController instance.
        """

        from savegem.app.gui.controller.players import PlayersController
        return PlayersController(_widget_manager)

    def test_get_data_when_game_players_configured(self, mocker: MockerFixture, _controller, activity_mock, 
                                                   games_config_mock, user_config_mock):

        def create_player(name: str):
            player = mocker.MagicMock(name=name)
            player.name = name
            player.email = f"{name.lower()}@test.com"

            return player

        first_player = create_player("First")
        second_player = create_player("Second")
        third_player = create_player("Third")
        forth_player = create_player("Forth")

        activity_mock.players = [first_player, third_player]
        games_config_mock.current.players = [second_player.email, third_player.email, forth_player.email]
        user_config_mock.__iter__.return_value = [first_player, second_player, third_player, forth_player]

        # Test with game_players configured
        # Only those should be displayed.
        controller_data = _controller._get_data()

        assert controller_data[0] == third_player
        # If not in-game then sorted alphabetically.
        assert controller_data[1] == forth_player
        assert controller_data[2] == second_player

        # Test without game_players configured.
        # In this case all application players should be listed.
        games_config_mock.current.players = []

        controller_data = _controller._get_data()

        assert controller_data[0] == first_player
        assert controller_data[1] == third_player
        assert controller_data[2] == forth_player
        assert controller_data[3] == second_player

    def test_resolve(self, mocker: MockerFixture, _controller):

        player_name = "Player Name"
        player_photo = "player_photo.jpg"

        player = mocker.MagicMock()
        player.short_name = player_name
        player.photo = player_photo

        name_result = _controller.resolve(player, "name")
        photo_result = _controller.resolve(player, "photo")
        invalid_result = _controller.resolve(player, "test")

        assert name_result == player_name
        assert photo_result == player_photo
        assert invalid_result is None

    def test_handle_player_card(self, mocker: MockerFixture, _controller, activity_mock):

        from savegem.app.gui.controller.players import PlayersController
        from savegem.app.gui.constants import QAttr

        player = mocker.MagicMock()
        player_card = mocker.MagicMock()

        # Test when player is not active.
        activity_mock.players = []

        _controller.handle__player_card(player_card, player)

        player_card.setProperty.assert_not_called()

        # Test when player is active.
        activity_mock.players = [player]

        _controller.handle__player_card(player_card, player)

        player_card.setProperty.assert_called_once_with(QAttr.Id, PlayersController.PlayerActive)
