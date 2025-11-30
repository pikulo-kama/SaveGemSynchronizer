import json
import pytest
from tests.test_data import GameTestData, PlayerTestData, ConfigTestData
from tests.util import json_to_bytes_io

NoActivity = {}
FirstPlayerActivity = {
    PlayerTestData.FirstPlayerEmail: [GameTestData.FirstGame]
}
SecondPlayerActivity = {
    PlayerTestData.FirstPlayerEmail: [GameTestData.FirstGame],
    PlayerTestData.SecondPlayerEmail: [GameTestData.FirstGame, GameTestData.SecondGame]
}


@pytest.fixture
def _activity(app_config, app_context_mock, user_config_mock, games_config_mock):
    from savegem.common.core.activity import Activity

    return Activity(app_context_mock)


def test_should_not_have_players_without_refresh(_activity):
    assert len(_activity.players) == 0


def test_should_retrieve_data_from_holder(_activity, holder_mock):
    from savegem.app.data import HolderObject

    holder_mock.get.return_value = NoActivity
    _activity.refresh()

    holder_mock.get.assert_called_with(HolderObject.Activity)
    assert len(_activity.players) == 0


def test_refresh_when_only_current_player(_activity, user_config_mock, holder_mock):
    holder_mock.get.return_value = FirstPlayerActivity
    _activity.refresh()

    assert len(_activity.players) == 1


def test_refresh_when_active_players(_activity, holder_mock):
    holder_mock.get.return_value = SecondPlayerActivity
    _activity.refresh()

    assert len(_activity.players) == 2

def test_update_when_has_active_games(_activity, holder_mock, gdrive_mock):

    from savegem.common.core.activity import Activity

    games = [GameTestData.FirstGame, GameTestData.SecondGame]

    gdrive_mock.download_file.return_value = json_to_bytes_io({**FirstPlayerActivity, **SecondPlayerActivity})
    _activity.update(games)

    update_args = gdrive_mock.update_file.call_args[0]
    file_id = update_args[0]
    data: dict = json.loads(update_args[1])

    assert file_id == ConfigTestData.ActivityLogFileId
    assert len(data.keys()) == 2

    first_player_email = PlayerTestData.FirstPlayerEmail
    second_player_email = PlayerTestData.SecondPlayerEmail

    # Verify that existing activity data was not modified.
    assert data.get(first_player_email) == games
    assert data.get(second_player_email) == SecondPlayerActivity.get(second_player_email)


def test_update_when_no_games(_activity, gdrive_mock):
    gdrive_mock.download_file.return_value = json_to_bytes_io(FirstPlayerActivity)
    _activity.update([])

    update_args = gdrive_mock.update_file.call_args[0]
    file_id = update_args[0]
    data: dict = json.loads(update_args[1])

    assert file_id == ConfigTestData.ActivityLogFileId
    # Previous user activity data was removed.
    assert len(data.keys()) == 0
