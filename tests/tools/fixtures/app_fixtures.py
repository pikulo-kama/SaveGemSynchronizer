import pytest
from pytest_mock import MockerFixture
from tests.test_data import GameTestData, LocaleTestData, ConfigTestData, PlayerTestData


@pytest.fixture
def app_context(mocker: MockerFixture, safe_module_patch):

    app_mock = mocker.MagicMock()
    safe_module_patch("app", app_mock)

    return app_mock


@pytest.fixture
def app_state_mock(mocker: MockerFixture, app_context):

    app_state_mock = mocker.MagicMock()
    type(app_state_mock).game_name = GameTestData.FirstGame
    type(app_state_mock).locale = LocaleTestData.FirstLocale
    type(app_state_mock).is_auto_mode = False

    app_context.state = app_state_mock

    return app_state_mock


@pytest.fixture
def app_config(mocker: MockerFixture, app_context):
    """
    Used to mock Google Drive configuration holder.
    """

    config_mock = mocker.MagicMock()
    type(config_mock).games_config_file_id = ConfigTestData.GameConfigFileId
    type(config_mock).activity_log_file_id = ConfigTestData.ActivityLogFileId

    app_context.config = config_mock

    return config_mock


@pytest.fixture
def games_config(mocker: MockerFixture, app_context):
    games_mock = mocker.MagicMock()
    games_mock.current.name = GameTestData.FirstGame
    games_mock.names = [GameTestData.FirstGame, GameTestData.SecondGame]

    app_context.games = games_mock

    return games_mock


@pytest.fixture
def user_config_mock(mocker: MockerFixture, app_context):
    user_mock = mocker.MagicMock()
    user_mock.machine_id = PlayerTestData.FirstPlayerMachineId
    user_mock.name = PlayerTestData.FirstPlayerName
    user_mock.email = PlayerTestData.FirstPlayerEmail

    app_context.user = user_mock

    return user_mock


@pytest.fixture
def activity_mock(mocker: MockerFixture, app_context):
    mock = mocker.MagicMock()
    app_context.activity = mock

    return mock
