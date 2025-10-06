import pytest
from savegem.common.core import ApplicationContext, app


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


def test_context_initialization(_activity, _app_state, _app_config, _game_config, _user_state):
    """
    Tests that ApplicationContext correctly instantiates all five components
    and verifies the private __link method is called for each.
    """

    context = ApplicationContext()

    # Verify all constructors were called once
    _activity.assert_called_once()
    _app_config.assert_called_once()
    _app_state.assert_called_once()
    _game_config.assert_called_once()
    _user_state.assert_called_once()

    # Check if app data is linked to context.
    _activity.return_value.link.assert_called_once_with(context),
    _app_config.return_value.link.assert_called_once_with(context),
    _app_state.return_value.link.assert_called_once_with(context),
    _game_config.return_value.link.assert_called_once_with(context),
    _user_state.return_value.link.assert_called_once_with(context),

    assert len(context._ApplicationContext__linked_entities) == 5  # noqa


def test_property_accessors(_activity, _app_state, _app_config, _game_config, _user_state):
    """
    Tests that all public properties return the correct, cached mock instance.
    """

    context = ApplicationContext()

    assert context.activity is _activity.return_value
    assert context.config is _app_config.return_value
    assert context.state is _app_state.return_value
    assert context.games is _game_config.return_value
    assert context.user is _user_state.return_value


def test_refresh_calls_all_linked_entities(_activity, _app_state, _app_config, _game_config, _user_state):
    """
    Tests that the refresh method calls refresh() on every linked entity.
    """

    context = ApplicationContext()
    context.refresh()

    _activity.return_value.refresh.assert_called_once()
    _app_config.return_value.refresh.assert_called_once()
    _app_state.return_value.refresh.assert_called_once()
    _game_config.return_value.refresh.assert_called_once()
    _user_state.return_value.refresh.assert_called_once()


def test_global_app_instance_exists():
    """
    Tests that the global 'app' singleton instance is defined and is of the correct type.
    """
    assert isinstance(app, ApplicationContext)
