from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from tests.test_data import GameTestData, PlayerTestData, ConfigTestData


@pytest.fixture
def _download_file_mock(gdrive_mock, tmp_path: Path):
    """
    Mocks GDrive.download_file to return the successful file data.
    """

    from tests.util import json_to_bytes_io

    gdrive_mock.download_file.return_value = json_to_bytes_io(
        [
            {
                "name": GameTestData.FirstGame,
                "localPath": str(tmp_path / GameTestData.FirstGame),
                "gdriveParentDirectoryId": "drive_A_id",
                "process": "GameA.exe",
                "allowAutoMode": True,
                "filesFilter": [".*\\.sav"],
                "players": [PlayerTestData.FirstPlayerEmail, PlayerTestData.SecondPlayerEmail]
            },
            {
                "name": GameTestData.SecondGame,
                "localPath": str(tmp_path / GameTestData.SecondGame),
                "gdriveParentDirectoryId": "drive_B_id",
                "process": "GameB.exe",
                "hidden": True
            },
            {
                "name": "Game C",
                "localPath": str(tmp_path / "GameC"),
                "gdriveParentDirectoryId": "drive_C_id",
                "process": "GameC.exe",
                "allowAutoMode": False,
                "players": [PlayerTestData.SecondPlayerEmail]
            },
            {
                "name": "Game D (No Filter)",
                "localPath": str(tmp_path / "GameD"),
                "gdriveParentDirectoryId": "drive_D_id",
                "process": "GameD.exe",
            }
        ]
    )


@pytest.fixture
def _games_config(app_context, app_config, user_config_mock, app_state_mock, _download_file_mock):

    from savegem.common.core.game_config import GameConfig

    game_config = GameConfig()
    game_config.link(app_context)

    return game_config


@pytest.fixture
def _game_path(tmp_path: Path):
    """
    Used to get local path of test game.
    """
    return str(tmp_path / "TestSaves")


@pytest.fixture
def _game(_game_path):
    """
    Provides a representative Game instance for testing.
    """

    from savegem.common.core.game_config import Game

    return Game(
        name="Test Game",
        process_name="Test.exe",
        local_path=_game_path,
        drive_directory="test_drive_id",
        files_filter=["save.*\\.dat", "save.*\\.bak", "config\\.ini"],
        auto_mode_allowed=True
    )


def test_download_success_and_filtering(gdrive_mock, _games_config):
    """
    Tests successful download and verifies filtering logic for players and hidden games.
    """

    _games_config.download()
    gdrive_mock.download_file.assert_called_once_with(ConfigTestData.GameConfigFileId)

    # Assert properties
    assert _games_config.empty is False
    assert len(_games_config.list) == 2
    assert _games_config.names == [GameTestData.FirstGame, "Game D (No Filter)"]

    # Game A should be present (player@example.com is in list)
    game_a = _games_config.by_name(GameTestData.FirstGame)
    assert game_a.name == GameTestData.FirstGame

    assert _games_config.by_name("Hidden Game B") is None

    # Game C should be filtered out since current user email is NOT in the players list
    assert _games_config.by_name("Game C") is None

    # Game D (No Filter) should be present (empty players list means all access)
    assert _games_config.by_name("Game D (No Filter)").name == "Game D (No Filter)"


def test_download_failure_raises_runtime_error_and_cleans_token(_games_config, gdrive_mock, resolve_app_data_mock,
                                                                delete_file_mock):
    """
    Tests the failure path when GDrive download fails.
    """

    from constants import File

    gdrive_mock.download_file.return_value = None

    with pytest.raises(RuntimeError) as error:
        _games_config.download()

    assert "Configuration file ID is invalid" in str(error.value)
    resolve_app_data_mock.assert_called_once_with(File.GDriveToken)
    delete_file_mock.assert_called_once()


def test_game_config_properties(_games_config):
    """
    Tests basic properties: list, names, empty, by_name, current.
    """

    from savegem.common.core.game_config import Game

    # Initial state
    assert _games_config.empty is True

    _games_config.download()

    assert len(_games_config.list) == 2
    assert isinstance(_games_config.list[0], Game)
    assert _games_config.names == [GameTestData.FirstGame, "Game D (No Filter)"]

    game_a = _games_config.by_name(GameTestData.FirstGame)
    assert game_a.process_name == "GameA.exe"
    assert _games_config.current.name == GameTestData.FirstGame
    assert _games_config.empty is False


def test_game_config_refresh_calls_game_meta_refresh(mocker: MockerFixture, _games_config):
    """
    Verifies that refresh() calls refresh on LocalMetadata for each game.
    """

    from savegem.common.core.save_meta import LocalMetadata

    # Mock the LocalMetadata.refresh method which is called via game.meta.local.refresh()
    mock_local_refresh = mocker.patch.object(LocalMetadata, "refresh")

    _games_config.download()
    _games_config.refresh()

    # We expect 2 calls, one for Game A and one for Game D
    assert mock_local_refresh.call_count == 2


def test_game_properties(_game):
    """
    Tests basic Game properties.
    """

    assert _game.name == "Test Game"
    assert _game.process_name == "Test.exe"
    assert _game.drive_directory == "test_drive_id"
    assert _game.auto_mode_allowed is True


def test_game_local_path_expands_vars(module_patch, _game, _game_path):
    """
    Verifies local_path uses os.path.expandvars.
    """

    mock_expandvars = module_patch(
        "os.path.expandvars",
        return_value="/user/home/TestSaves"
    )

    assert _game.local_path == "/user/home/TestSaves"
    mock_expandvars.assert_called_once_with(_game_path)


def test_game_metadata_file_path(_game, module_patch):
    """
    Verifies metadata_file_path is constructed correctly.
    """

    mock_expandvars = module_patch(
        "os.path.expandvars",
        return_value="/user/home/TestSaves"
    )
    mock_join = module_patch(
        "os.path.join",
        return_value="/user/home/TestSaves/SaveGemMetadata.json"
    )

    path = _game.metadata_file_path

    assert path == "/user/home/TestSaves/SaveGemMetadata.json"
    mock_join.assert_called_once_with(mock_expandvars.return_value, "SaveGemMetadata.json")


def test_game_filter_patterns_with_filter(_game):
    """
    Tests filter_patterns when filters are defined.
    """

    patterns = _game.filter_patterns

    assert len(patterns) == 3
    assert patterns[0].pattern == "save.*\\.dat"
    assert patterns[1].pattern == "save.*\\.bak"
    assert patterns[2].pattern == "config\\.ini"

    assert patterns[0].match("save001.dat") is not None
    assert patterns[0].match("config.ini") is None


def test_game_filter_patterns_no_filter(_game_path):
    """
    Tests filter_patterns when the filter list is empty (should default to ".*").
    """

    from savegem.common.core.game_config import Game

    # Arrange: Create a Game instance with an empty filter list
    game_no_filter = Game(
        name="NoFilter",
        process_name="N/A",
        local_path=_game_path,
        drive_directory="N/A",
        files_filter=[],  # Empty list
        auto_mode_allowed=True
    )

    patterns = game_no_filter.filter_patterns

    assert len(patterns) == 1
    # Should default to matching all files (.*)
    assert patterns[0].pattern == ".*"
    assert patterns[0].match("anyfile.txt") is not None


def test_game_file_list_filtering(_game, module_patch):
    """
    Tests file_list property, ensuring files are filtered by regex.
    """

    # 1. Arrange: Mock the local directory path and content
    module_patch(
        "os.path.expandvars",
        return_value="/user/home/TestSaves"
    )

    mock_listdir = module_patch(
        "os.listdir",
        return_value=[
            "save_100.dat",  # Matches pattern 1
            "config.ini",  # Matches pattern 2
            "temp.log",  # No match
            "save_001.bak",  # Matches pattern 1
            "metadata_file.json",  # No match
        ]
    )

    # Mock os.path.join to return clean paths
    mock_join = module_patch(
        "os.path.join",
        side_effect=lambda *args: "/".join(args)
    )

    # 2. Act: Convert the generator to a list
    file_list = list(_game.file_list)

    # 3. Assert: Only expected files should be included, and they should be sorted
    assert file_list == [
        "/user/home/TestSaves/config.ini",
        "/user/home/TestSaves/save_001.bak",
        "/user/home/TestSaves/save_100.dat"
    ]

    mock_listdir.assert_called_once_with("/user/home/TestSaves")
    # Verify join was called for each included file
    assert mock_join.call_count == 3
