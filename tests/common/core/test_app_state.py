import pytest
from pytest_mock import MockerFixture

from tests.test_data import GameTestData, LocaleTestData


@pytest.fixture(autouse=True)
def _setup(editable_json_config_holder_mock, resolve_app_data_mock):

    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder
    from savegem.common.core import AppState

    mock_holder = MockJsonConfigHolder({
        AppState.SelectedGame: GameTestData.FirstGame,
        AppState.SelectedLocale: LocaleTestData.FirstLocale,
        AppState.IsAutoMode: False
    })

    editable_json_config_holder_mock.return_value = mock_holder


@pytest.fixture
def _app_state(mocker: MockerFixture, app_context, app_config, games_config):

    from savegem.common.core import AppState

    state_change_callback = mocker.Mock()

    state = AppState()
    state.link(app_context)
    state.on_change(state_change_callback)

    app_state_tools = mocker.MagicMock()
    app_state_tools.instance = state
    app_state_tools.callback = state_change_callback
    app_state_tools.set_value = mocker.spy(state._AppState__state, "set_value")  # noqa

    return app_state_tools


def test_should_call_callback_when_changing_game(_app_state):

    from savegem.common.core import AppState

    _app_state.instance.game_name = GameTestData.SecondGame

    _app_state.callback.assert_called_once()
    _app_state.set_value.assert_called_with(AppState.SelectedGame, GameTestData.SecondGame)
    assert _app_state.instance.game_name == GameTestData.SecondGame


def test_should_call_callback_when_changing_locale(_app_state):

    from savegem.common.core import AppState

    _app_state.instance.locale = LocaleTestData.FirstLocale

    _app_state.callback.assert_called_once()
    _app_state.set_value.assert_called_with(AppState.SelectedLocale, LocaleTestData.FirstLocale)
    assert _app_state.instance.locale == LocaleTestData.FirstLocale


def test_should_call_callback_when_changing_auto_mode(_app_state):

    from savegem.common.core import AppState

    _app_state.instance.is_auto_mode = True

    _app_state.callback.assert_called_once()
    _app_state.set_value.assert_called_with(AppState.IsAutoMode, True)
    assert _app_state.instance.is_auto_mode is True


def test_should_not_call_callback_when_changing_width(_app_state):

    from savegem.common.core import AppState

    width = 1920
    _app_state.instance.width = width

    _app_state.callback.assert_not_called()
    _app_state.set_value.assert_called_with(AppState.WindowWidth, width)
    assert _app_state.instance.width == width


def test_should_not_call_callback_when_changing_height(_app_state):

    from savegem.common.core import AppState

    height = 1080
    _app_state.instance.height = height

    _app_state.callback.assert_not_called()
    _app_state.set_value.assert_called_with(AppState.WindowHeight, height)
    assert _app_state.instance.height == height


def test_should_get_first_game_if_not_in_state(_app_state):

    from savegem.common.core import AppState

    _app_state.instance.game_name = None
    game_name = _app_state.instance.game_name

    _app_state.set_value.assert_called_with(AppState.SelectedGame, game_name)
    assert game_name == GameTestData.FirstGame


def test_should_get_default_locale_if_not_in_state(_app_state):

    from savegem.common.core import AppState

    _app_state.instance.locale = None
    locale = _app_state.instance.locale

    _app_state.set_value.assert_called_with(AppState.SelectedLocale, locale)
    assert locale == LocaleTestData.FirstLocale


def test_refresh(_app_state, editable_json_config_holder_mock):
    _app_state.instance.refresh()
    # Once for initialization and once for refresh.
    editable_json_config_holder_mock.call_count = 2
