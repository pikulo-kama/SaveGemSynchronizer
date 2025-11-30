import pytest
from pytest_mock import MockerFixture
from tests.test_data import GameTestData, LocaleTestData, ConfigTestData, PlayerTestData


@pytest.fixture
def app_context_mock(mocker: MockerFixture, safe_module_patch, logger_mock):

    app_mock = mocker.MagicMock()
    safe_module_patch("app", return_value=app_mock)

    return app_mock


@pytest.fixture
def app_state_mock(mocker: MockerFixture, app_context_mock):

    app_state_mock = mocker.MagicMock()
    type(app_state_mock).game_name = GameTestData.FirstGame
    type(app_state_mock).locale = LocaleTestData.FirstLocale
    type(app_state_mock).is_auto_mode = False

    app_state_mock.app = app_context_mock
    app_context_mock.state = app_state_mock

    return app_state_mock


@pytest.fixture(autouse=True)
def app_config(mocker: MockerFixture, app_context_mock):
    """
    Used to mock Google Drive configuration holder.
    """

    config_mock = mocker.MagicMock()
    type(config_mock).games_config_file_id = ConfigTestData.GameConfigFileId
    type(config_mock).activity_log_file_id = ConfigTestData.ActivityLogFileId
    type(config_mock).users_config_file_id = ConfigTestData.UsersConfigFileId

    config_mock.app = app_context_mock
    app_context_mock.config = config_mock

    return config_mock


@pytest.fixture
def games_config_mock(mocker: MockerFixture, app_context_mock):
    games_mock = mocker.MagicMock()
    first_game = mocker.MagicMock()
    second_game = mocker.MagicMock()

    first_game.name = GameTestData.FirstGame
    first_game.settings.auto_mode = True
    second_game.name = GameTestData.SecondGame
    second_game.settings.auto_mode = False

    games_mock.current = first_game
    games_mock.__iter__.return_value = [first_game, second_game]
    games_mock.names = [GameTestData.FirstGame, GameTestData.SecondGame]

    # For testing purposes, to be able to reference
    # games directly.
    games_mock.first = first_game
    games_mock.second = second_game

    games_mock.app = app_context_mock
    app_context_mock.games = games_mock

    return games_mock


@pytest.fixture
def user_config_mock(mocker: MockerFixture, app_context_mock):
    user_mock = mocker.MagicMock()
    user_mock.current.id = PlayerTestData.FirstPlayerId
    user_mock.current.name = PlayerTestData.FirstPlayerName
    user_mock.current.email = PlayerTestData.FirstPlayerEmail

    user_mock.app = app_context_mock
    app_context_mock.users = user_mock

    return user_mock


@pytest.fixture
def activity_mock(mocker: MockerFixture, app_context_mock):
    mock = mocker.MagicMock()
    mock.app = app_context_mock
    app_context_mock.activity = mock

    return mock


@pytest.fixture
def flags_mock(module_patch):
    return module_patch("flags").return_value


@pytest.fixture
def holder_mock(module_patch):
    return module_patch("holder").return_value
