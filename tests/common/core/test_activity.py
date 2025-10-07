import json
import pytest

from tests.test_data import GameTestData, PlayerTestData, ConfigTestData
from tests.util import json_to_bytes_io


NoActivity = {}


@pytest.fixture
def _first_player_activity():

    from savegem.common.core.activity import Activity

    return {
        PlayerTestData.FirstPlayerMachineId: {
            Activity.NAME_PROP: PlayerTestData.FirstPlayerName,
            Activity.GAMES_PROP: [GameTestData.FirstGame]
        }
    }


@pytest.fixture
def _second_player_activity():

    from savegem.common.core.activity import Activity

    return {
        PlayerTestData.SecondPlayerMachineId: {
            Activity.NAME_PROP: PlayerTestData.SecondPlayerName,
            Activity.GAMES_PROP: [GameTestData.FirstGame]
        }
    }


@pytest.fixture
def _multiple_players_activity(_first_player_activity, _second_player_activity):
    return {
        **_first_player_activity,
        **_second_player_activity
    }


@pytest.fixture
def _activity(app_config, app_context, user_config_mock, games_config):

    from savegem.common.core.activity import Activity

    activity = Activity()
    activity.link(app_context)

    return activity


@pytest.fixture
def _mock_download_file(gdrive_mock):
    return lambda data: gdrive_mock.download_file.configure_mock(
        side_effect=lambda file_id: json_to_bytes_io(data)
    )


def test_should_not_have_players_without_refresh(_activity):
    assert len(_activity.players) == 0


def test_should_use_config_file_id_when_downloading(_activity, _mock_download_file, gdrive_mock):
    _mock_download_file(NoActivity)
    _activity.refresh()

    gdrive_mock.download_file.assert_called_with(ConfigTestData.ActivityLogFileId)


def test_refresh_when_no_active_players(_activity, _mock_download_file, gdrive_mock):
    _mock_download_file(NoActivity)
    _activity.refresh()

    assert len(_activity.players) == 0


def test_refresh_when_only_current_player(_activity, user_config_mock, _mock_download_file, gdrive_mock,
                                          _first_player_activity):
    _mock_download_file(_first_player_activity)
    _activity.refresh()

    # Current user should not be considered.
    assert len(_activity.players) == 0


def test_refresh_when_active_players(_activity, _mock_download_file, gdrive_mock, _second_player_activity):
    _mock_download_file(_second_player_activity)
    _activity.refresh()

    # Current user should not be considered.
    assert len(_activity.players) == 1


def test_refresh_when_activity_contains_not_selected_game(_activity, _mock_download_file, gdrive_mock, games_config,
                                                          _second_player_activity):
    _mock_download_file(_second_player_activity)
    games_config.current.name = GameTestData.SecondGame
    _activity.refresh()

    # Only activity data for current game should be considered.
    assert len(_activity.players) == 0


def test_update_when_has_active_games(_activity, _mock_download_file, gdrive_mock, _second_player_activity):

    from savegem.common.core.activity import Activity

    games = [GameTestData.FirstGame, GameTestData.SecondGame]

    _mock_download_file(_second_player_activity)
    _activity.update(games)

    update_args = gdrive_mock.update_file.call_args[0]
    file_id = update_args[0]
    data: dict = json.loads(update_args[1])

    assert file_id == ConfigTestData.ActivityLogFileId
    assert len(data.keys()) == 2

    first_machine_id = PlayerTestData.FirstPlayerMachineId
    second_machine_id = PlayerTestData.SecondPlayerMachineId

    # Verify that existing activity data was not modified.
    assert data.get(second_machine_id) == _second_player_activity.get(second_machine_id)
    assert data.get(first_machine_id, {}).get(Activity.NAME_PROP) == PlayerTestData.FirstPlayerName
    assert data.get(first_machine_id, {}).get(Activity.GAMES_PROP) == games


def test_update_when_no_games(_activity, _mock_download_file, gdrive_mock, _first_player_activity):
    _mock_download_file(_first_player_activity)
    _activity.update([])

    update_args = gdrive_mock.update_file.call_args[0]
    file_id = update_args[0]
    data: dict = json.loads(update_args[1])

    assert file_id == ConfigTestData.ActivityLogFileId
    # Previous user activity data was removed.
    assert len(data.keys()) == 0
