import pytest


@pytest.fixture
def _activity(module_patch):
    return module_patch("Activity", autospec=True)


@pytest.fixture
def _app_config(module_patch):
    return module_patch("AppConfig", autospec=True)


@pytest.fixture
def _app_state(module_patch):
    return module_patch("AppState", autospec=True)


@pytest.fixture
def _game_config(module_patch):
    return module_patch("GameConfig", autospec=True)


@pytest.fixture
def _user_state(module_patch):
    return module_patch("UserState", autospec=True)


def test_property_accessors(_activity, _app_state, _app_config, _game_config, _user_state):
    """
    Tests that all public properties return the correct, cached mock instance.
    """

    from savegem.common.core.context import ApplicationContext

    context = ApplicationContext()

    assert context.activity is _activity.return_value
    assert context.config is _app_config.return_value
    assert context.state is _app_state.return_value
    assert context.games is _game_config.return_value
    assert context.users is _user_state.return_value
