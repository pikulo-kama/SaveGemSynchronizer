import pytest
from pytest_mock import MockerFixture

from tests.test_data import GameTestData, LocaleTestData


@pytest.fixture(autouse=True)
def _setup(editable_json_config_holder_mock, resolve_app_data_mock, locales_mock):

    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder
    from savegem.common.core.app_state import AppState

    mock_holder = MockJsonConfigHolder({
        AppState.SelectedGame: GameTestData.FirstGame,
        AppState.SelectedLocale: LocaleTestData.FirstLocale,
        AppState.IsAutoMode: False
    })

    editable_json_config_holder_mock.return_value = mock_holder
    locales_mock.return_value = [LocaleTestData.FirstLocale, LocaleTestData.SecondLocale]


@pytest.fixture
def _state_change_callback(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def _set_value_spy(mocker: MockerFixture, _app_state):
    return mocker.spy(_app_state._AppState__state, "set_value")  # noqa


@pytest.fixture
def _app_state(app_context, app_config, games_config, _state_change_callback):

    from savegem.common.core.app_state import AppState

    state = AppState()
    state.link(app_context)
    state.on_change(_state_change_callback)

    return state


def test_should_call_callback_when_changing_game(_app_state, _state_change_callback, _set_value_spy):

    from savegem.common.core.app_state import AppState

    _app_state.game_name = GameTestData.SecondGame

    _state_change_callback.assert_called_once()
    _set_value_spy.assert_called_with(AppState.SelectedGame, GameTestData.SecondGame)
    assert _app_state.game_name == GameTestData.SecondGame


def test_should_call_callback_when_changing_locale(_app_state, _state_change_callback, _set_value_spy):

    from savegem.common.core.app_state import AppState

    _app_state.locale = LocaleTestData.FirstLocale

    _state_change_callback.assert_called_once()
    _set_value_spy.assert_called_with(AppState.SelectedLocale, LocaleTestData.FirstLocale)
    assert _app_state.locale == LocaleTestData.FirstLocale


def test_should_call_callback_when_changing_auto_mode(_app_state, _state_change_callback, _set_value_spy):

    from savegem.common.core.app_state import AppState

    _app_state.is_auto_mode = True

    _state_change_callback.assert_called_once()
    _set_value_spy.assert_called_with(AppState.IsAutoMode, True)
    assert _app_state.is_auto_mode is True


def test_should_not_call_callback_when_changing_width(_app_state, _state_change_callback, _set_value_spy):

    from savegem.common.core.app_state import AppState

    width = 1920
    _app_state.width = width

    _state_change_callback.assert_not_called()
    _set_value_spy.assert_called_with(AppState.WindowWidth, width)
    assert _app_state.width == width


def test_should_not_call_callback_when_changing_height(_app_state, _state_change_callback, _set_value_spy):

    from savegem.common.core.app_state import AppState

    height = 1080
    _app_state.height = height

    _state_change_callback.assert_not_called()
    _set_value_spy.assert_called_with(AppState.WindowHeight, height)
    assert _app_state.height == height


def test_should_get_first_game_if_not_in_state(_app_state, _set_value_spy):

    from savegem.common.core.app_state import AppState

    _app_state.game_name = None
    game_name = _app_state.game_name

    _set_value_spy.assert_called_with(AppState.SelectedGame, game_name)
    assert game_name == GameTestData.FirstGame


def test_should_get_default_locale_if_not_in_state(_app_state, _set_value_spy, prop_mock):

    from savegem.common.core.app_state import AppState

    prop_mock.return_value = LocaleTestData.FirstLocale

    _app_state.locale = None
    locale = _app_state.locale

    _set_value_spy.assert_called_with(AppState.SelectedLocale, locale)
    assert locale == LocaleTestData.FirstLocale


def test_refresh(_app_state, editable_json_config_holder_mock):
    _app_state.refresh()
    # Once for initialization and once for refresh.
    editable_json_config_holder_mock.call_count = 2
