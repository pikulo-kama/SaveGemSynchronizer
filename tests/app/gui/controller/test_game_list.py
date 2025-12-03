import pytest
from unittest.mock import call
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestGameListController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, games_config_mock, app_state_mock, _game_list_data, _push_button_mock):

        games_config_mock.__iter__.return_value = _game_list_data
        games_config_mock.current = _game_list_data[0]
        app_state_mock.game_name = _game_list_data[0].name

        _push_button_mock.side_effect = [game.button for game in _game_list_data]

    @pytest.fixture
    def _game_list_data(self, _game_a, _game_b, _game_c, _game_d):
        return [_game_a, _game_b, _game_c, _game_d]

    @pytest.fixture
    def _game_a(self, mocker: MockerFixture):
        from savegem.common.core.save_meta import SyncStatus
        return self._create_game(mocker, "GameA", SyncStatus.UpToDate, True)

    @pytest.fixture
    def _game_b(self, mocker: MockerFixture):
        from savegem.common.core.save_meta import SyncStatus
        return self._create_game(mocker, "GameB", SyncStatus.NeedsUpload)

    @pytest.fixture
    def _game_c(self, mocker: MockerFixture):
        from savegem.common.core.save_meta import SyncStatus
        return self._create_game(mocker, "GameC", SyncStatus.NoInformation)

    @pytest.fixture
    def _game_d(self, mocker: MockerFixture):
        from savegem.common.core.save_meta import SyncStatus
        return self._create_game(mocker, "GameD", SyncStatus.UpToDate)

    @staticmethod
    def _create_game(mocker: MockerFixture, name: str, sync_status, is_current: bool = False):
        game = mocker.MagicMock()
        game.name = name
        game.meta.sync_status = sync_status
        game.is_current = is_current

        game.button = mocker.MagicMock()

        return game

    @pytest.fixture
    def _game_list(self, mocker: MockerFixture):
        """
        Mocks the QScrollableWidget passed to refresh.
        """
        return mocker.MagicMock()

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the GameListController instance.
        """

        from savegem.app.gui.controller.game_list import GameListController
        return GameListController(_widget_manager)

    @pytest.fixture
    def _game_change_worker_mock(self, module_patch):
        return module_patch("GameChangeWorker")

    def test_refresh_renders_list_correctly(self, _controller, _widget_manager, _game_list, _game_list_data,
                                            _push_button_mock, _spacer_mock):
        """
        Tests that refresh clears children, iterates through games, sets properties,
        and adds buttons and a spacer.
        """

        from savegem.app.gui.constants import QBool
        from savegem.common.core.save_meta import SyncStatus

        _controller.refresh(_game_list)

        _widget_manager.remove_child_widgets.assert_called_once_with(_game_list)
        assert _push_button_mock.call_count == 4
        add_widget_mock = _game_list.layout.return_value.add_dynamic_widget

        for game in _game_list_data:

            # General checks
            game.button.setText.assert_called_once_with(game.name)
            game.button.clicked.connect.assert_called_once()
            add_widget_mock.assert_any_call(game.button)

            # Property Check: SELECTED (Only GameA)
            if game.name == "GameA":
                game.button.setProperty.assert_any_call("selected", QBool(True))
            else:
                assert call("selected", QBool(True)) not in game.button.setProperty.call_args_list

            # Property Check: WARNING (GameB, GameC)
            if game.meta.sync_status != SyncStatus.UpToDate:
                game.button.setProperty.assert_any_call("warning", QBool(True))
            else:
                assert call("warning", QBool(True)) not in game.button.setProperty.call_args_list

        # 3. Assert QSpacer is added last
        _spacer_mock.assert_called_once()
        add_widget_mock.assert_any_call(_spacer_mock.return_value)
        assert add_widget_mock.call_count == 5  # 4 buttons + 1 spacer

    def test_change_game_early_exit(self, _controller, _do_work_mock):
        """
        Tests that __change_game returns early if the new game is the current game (matches app().state.game_name).
        """

        _controller._GameListController__change_game("GameA")  # noqa
        _do_work_mock.assert_not_called()

    def test_change_game_starts_worker(self, _controller, _widget_manager, _do_work_mock, _game_change_worker_mock):
        """
        Tests that __change_game instantiates and executes GameChangeWorker when the game is changed.
        """

        from savegem.app.gui.constants import UIRefreshEvent

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

        _widget_manager.gui.refresh.assert_called_once_with(UIRefreshEvent.GameSelectionChange)
