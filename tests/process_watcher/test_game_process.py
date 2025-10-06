import pytest

from savegem.process_watcher.game_process import _get_active_games, get_running_game_processes, GameProcess  # noqa
from tests.tools.mocks.mock_game import MockGame
from tests.tools.mocks.mock_process import MockProcess

_first_game = MockGame(
    name="First Game",
    process_name="FirstGame.exe",
    auto_mode_allowed=True
)
_first_process = MockProcess(_first_game.process_name)

_second_game = MockGame(
    name="Second Game",
    process_name="SecondGame.exe",
    auto_mode_allowed=False
)
_second_process = MockProcess(_second_game.process_name)


@pytest.fixture(autouse=True)
def _setup_dependencies(app_context, games_config):
    type(games_config).list = [_first_game, _second_game]

    games_config.by_name.side_effect = lambda name: {
        _first_game.name: _first_game,
        _second_game.name: _second_game,
    }[name]


@pytest.fixture
def _active_games_mock(module_patch):
    return module_patch("_get_active_games")


@pytest.fixture
def _mock_previous_games(module_patch):
    return lambda games: module_patch("_previous_game_names", new=games, create=True)


def test_should_get_active_game_objects(module_patch):
    get_run_processes_mock = module_patch("get_running_processes")
    get_run_processes_mock.return_value = [_first_process, _second_process]

    active_games = _get_active_games()

    assert len(active_games) == 2
    assert active_games[0] == _first_game.name
    assert active_games[1] == _second_game.name


def test_when_no_active_processes(_active_games_mock):
    _active_games_mock.return_value = []
    assert len(get_running_game_processes()) == 0


def test_when_process_has_started(_active_games_mock, _mock_previous_games):
    _mock_previous_games([])
    _active_games_mock.return_value = [_first_game.name]

    active_processes = get_running_game_processes()

    assert len(active_processes) == 1
    assert isinstance(active_processes[0], GameProcess)
    assert active_processes[0].game == _first_game
    assert active_processes[0].has_started


def test_when_process_has_ended(_active_games_mock, _mock_previous_games):
    _mock_previous_games([_first_game.name])
    _active_games_mock.return_value = []

    active_processes = get_running_game_processes()

    assert len(active_processes) == 1
    assert active_processes[0].game == _first_game
    assert active_processes[0].has_closed


def test_when_process_is_idle(_active_games_mock, _mock_previous_games):
    _mock_previous_games([_first_game.name])
    _active_games_mock.return_value = [_first_game.name]

    active_processes = get_running_game_processes()

    assert len(active_processes) == 1
    assert active_processes[0].game == _first_game
    assert active_processes[0].is_running
    assert not active_processes[0].has_started
    assert not active_processes[0].has_closed
