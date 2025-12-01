from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from tests.test_data import GameTestData, LocaleTestData


class TestAppState:

    @pytest.fixture(autouse=True)
    def _setup(self, locales_mock, db_table_mock):
        locales_mock.return_value = [LocaleTestData.FirstLocale, LocaleTestData.SecondLocale]


    @pytest.fixture
    def _state_change_callback(self, mocker: MockerFixture):
        return mocker.Mock()


    @pytest.fixture
    def _app_state(self, app_context_mock, app_config_mock, games_config_mock, _state_change_callback):

        from savegem.common.core.app_state import AppState

        state = AppState(app_context_mock)
        state.on_change(_state_change_callback)

        return state


    def test_should_call_callback_when_changing_game(self, _app_state, _state_change_callback, db_table_mock):

        from savegem.common.core.app_state import AppState

        _app_state.game_name = GameTestData.SecondGame

        _state_change_callback.assert_called_once()
        db_table_mock.get_first.return_value = GameTestData.SecondGame

        db_table_mock.set_first.assert_called_with(AppState.SelectedGame, GameTestData.SecondGame)
        assert _app_state.game_name == GameTestData.SecondGame

        db_table_mock.get_first.assert_called_once_with(AppState.SelectedGame)


    def test_should_call_callback_when_changing_locale(self, _app_state, _state_change_callback, db_table_mock):

        from savegem.common.core.app_state import AppState

        _app_state.locale = LocaleTestData.FirstLocale

        _state_change_callback.assert_called_once()
        db_table_mock.get_first.return_value = LocaleTestData.FirstLocale

        db_table_mock.set_first.assert_called_with(AppState.SelectedLocale, LocaleTestData.FirstLocale)
        assert _app_state.locale == LocaleTestData.FirstLocale

        db_table_mock.get_first.assert_called_once_with(AppState.SelectedLocale)


    def test_should_call_callback_when_changing_color_theme(self, _app_state, db_table_mock):

        from savegem.common.core.app_state import AppState
        from savegem.app.gui.style import ColorMode

        _app_state.color_theme = ColorMode.Dark

        db_table_mock.get_first.return_value = ColorMode.Dark

        db_table_mock.set_first.assert_called_with(AppState.ColorTheme, ColorMode.Dark)
        assert _app_state.color_theme == ColorMode.Dark

        db_table_mock.get_first.assert_called_once_with(AppState.ColorTheme)


    def test_should_call_callback_when_changing_time_format(self, _app_state, db_table_mock):

        from savegem.common.core.app_state import AppState
        from constants import TimeFormat

        _app_state.time_format = TimeFormat.Regular

        db_table_mock.get_first.return_value = TimeFormat.Regular

        db_table_mock.set_first.assert_called_with(AppState.TimeFormatId, TimeFormat.Regular)
        assert _app_state.time_format == TimeFormat.Regular

        db_table_mock.get_first.assert_called_once_with(AppState.TimeFormatId)


    def test_should_use_default_time_format_if_not_provided(self, _app_state, db_table_mock):

        from constants import TimeFormat

        db_table_mock.get_first.return_value = None
        assert _app_state.time_format == TimeFormat.Military


    def test_should_get_first_game_if_not_in_state(self, _app_state, db_table_mock):

        from savegem.common.core.app_state import AppState

        _app_state.game_name = None
        game_name = _app_state.game_name

        db_table_mock.set_first.assert_called_with(AppState.SelectedGame, game_name)
        assert game_name == GameTestData.FirstGame


    def test_should_get_default_locale_if_not_in_state(self, _app_state, db_table_mock, prop_mock):

        from savegem.common.core.app_state import AppState

        prop_mock.return_value = LocaleTestData.FirstLocale

        _app_state.locale = None
        locale = _app_state.locale

        db_table_mock.set_first.assert_called_with(AppState.SelectedLocale, locale)
        assert locale == LocaleTestData.FirstLocale


    def test_should_create_temporary_record_when_no_user_data(self, app_context_mock, db_table_mock):

        from savegem.common.core.app_state import AppState

        app_context_mock.users.current = None

        app_state = AppState(app_context_mock)
        app_state.refresh()

        db_table_mock.where.assert_has_calls([
            call("user_id = ?", AppState.TemporaryUser),
            call("user_id = ?", AppState.TemporaryUser)
        ], any_order=True)


    def test_refresh(self, _app_state, db_mock):
        _app_state.refresh()

        # Once for initialization and once for refresh.
        db_mock.table.call_count = 2
