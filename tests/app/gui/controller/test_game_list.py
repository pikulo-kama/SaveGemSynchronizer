import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestGameListController(WidgetControllerTest):

    @pytest.fixture
    def _game_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _game(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the GameListController instance.
        """

        from src.savegem import GameListController
        return GameListController(_widget_manager)

    @pytest.fixture
    def _game_change_worker_mock(self, module_patch):
        return module_patch("GameChangeWorker")

    def test_get_data(self, _controller, games_config_mock):
        assert _controller._get_data() == games_config_mock

    def test_handle_game_option_for_current_game(self, _controller, _game_button, _game, games_config_mock):

        from src.savegem import GameListController
        from src.savegem.common.core.save_meta import SyncStatus
        from src.savegem import QBool

        games_config_mock.current = _game
        _game.meta.sync_status = SyncStatus.UpToDate

        _controller.handle__game_option(_game_button, _game)

        assert _game_button.setProperty.call_count == 1
        _game_button.setProperty.assert_called_once_with(GameListController.GameOptionSelected, QBool(True))

    def test_handle_game_option_for_outdated_game(self, _controller, _game_button, _game, games_config_mock):

        from src.savegem import GameListController
        from src.savegem.common.core.save_meta import SyncStatus
        from src.savegem import QBool

        _game.meta.sync_status = SyncStatus.NeedsUpload

        _controller.handle__game_option(_game_button, _game)

        assert _game_button.setProperty.call_count == 1
        _game_button.setProperty.assert_called_once_with(GameListController.GameOptionWarning, QBool(True))

    def test_handle_game_option_binds_callback(self, mocker: MockerFixture, _controller, _game_button, _game,
                                               games_config_mock):
        game_name = "Game"
        change_game_mock = mocker.patch.object(_controller, "_GameListController__change_game")
        _game.name = game_name

        _controller.handle__game_option(_game_button, _game)

        change_name_callback = _game_button.clicked.connect.call_args[0][0]
        change_name_callback()

        change_game_mock.assert_called_once_with(game_name)

    def test_resolve(self, _controller, _game):

        game_name = "Game"
        _game.name = game_name

        invalid_param_result = _controller.resolve(_game, "test", 1, 2, 3, a=1, b=2, c=3)
        valid_param_result = _controller.resolve(_game, "name", 1, 2, 3, a=1, b=2, c=3)

        assert invalid_param_result is None
        assert valid_param_result == game_name

    def test_should_not_change_game_if_same(self, _controller, app_state_mock, _game_change_worker_mock, _do_work_mock):

        game_name = "Game"
        app_state_mock.game_name = game_name

        _controller._GameListController__change_game(game_name)  # noqa

        _game_change_worker_mock.assert_not_called()
        _do_work_mock.assert_not_called()

    def test_change_game_starts_worker(self, _controller, _widget_manager, _do_work_mock, _game_change_worker_mock):
        """
        Tests that __change_game instantiates and executes GameChangeWorker when the game is changed.
        """

        from src.savegem import UIRefreshEvent

        new_game_name = "GameX"

        # ACT: Change game to "GameX"
        _controller._GameListController__change_game(new_game_name)  # noqa

        # 1. Assert Worker instantiation
        _game_change_worker_mock.assert_called_once_with(new_game_name)

        # 2. Assert Worker execution
        _do_work_mock.assert_called_once_with(_game_change_worker_mock.return_value)

        # 3. Assert refresh signal connection
        _game_change_worker_mock.return_value.finished.connect.assert_called_once()

        # Verify the lambda connection for manager.gui.refresh
        refresh_callback = _game_change_worker_mock.return_value.finished.connect.call_args[0][0]
        refresh_callback()

        _widget_manager.event_refresh.assert_called_once_with(UIRefreshEvent.GameSelectionChange)
