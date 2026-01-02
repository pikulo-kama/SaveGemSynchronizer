from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from tests.test_data import GameTestData, PlayerTestData


class GameModuleTestHelper:

    @pytest.fixture(autouse=True)
    def _module_setup(self, db_table_mock, url_retrieve_mock):
        pass

    @pytest.fixture
    def _game_path(self, tmp_path: Path):
        """
        Used to get local path of test game.
        """
        return str(tmp_path / "TestSaves")

    @pytest.fixture
    def _game(self, _game_path, _games_config):
        """
        Provides a representative Game instance for testing.
        """

        from savegem.common.core.game_config import Game

        return Game(
            game_config=_games_config,
            name="Test Game",
            process_name="Test.exe",
            logo="test",
            local_path=_game_path,
            drive_directory="test_drive_id",
            files_filter=["save.*\\.dat", "save.*\\.bak", "service_info\\.ini"],
            auto_mode_allowed=True,
            players=[PlayerTestData.FirstPlayerEmail]
        )


    @pytest.fixture
    def _games_config(self, app_context_mock, app_config_mock, user_config_mock, app_state_mock):
        from savegem.common.core.game_config import GameConfig

        return GameConfig(app_context_mock)

class TestGameConfig(GameModuleTestHelper):

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path: Path, holder_mock, resolve_temp_resource_mock):
        """
        Mocks GDrive.download_file to return the successful file data.
        """

        resolve_temp_resource_mock.side_effect = lambda path: f"/resource/path/{path}"

        holder_mock.get.return_value = [
            {
                "name": GameTestData.FirstGame,
                "localPath": str(tmp_path / GameTestData.FirstGame),
                "logo": "https://test123/logo",
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


    def test_download_success_and_filtering(self, holder_mock, _games_config):
        """
        Tests successful download and verifies filtering logic for players and hidden games.
        """

        from savegem.constants import HolderObject

        _games_config.initialize()
        holder_mock.get.assert_called_once_with(HolderObject.GamesConfig)

        # Assert properties
        assert _games_config.empty is False
        assert len(_games_config) == 2
        assert _games_config.names == [GameTestData.FirstGame, "Game D (No Filter)"]

        # Game A should be present (player@example.com is in list)
        game_a = _games_config.by_name(GameTestData.FirstGame)
        assert game_a.name == GameTestData.FirstGame

        assert _games_config.by_name("Hidden Game B") is None

        # Game C should be filtered out since current user email is NOT in the players list
        assert _games_config.by_name("Game C") is None

        # Game D (No Filter) should be present (empty players list means all access)
        assert _games_config.by_name("Game D (No Filter)").name == "Game D (No Filter)"


    def test_download_failure_raises_runtime_error_and_cleans_token(self, _games_config, holder_mock,
                                                                    resolve_app_data_mock, delete_file_mock):
        """
        Tests the failure path when GDrive download fails.
        """

        from savegem.constants import File

        holder_mock.get.return_value = None

        with pytest.raises(RuntimeError) as error:
            _games_config.initialize()

        assert "Configuration file ID is invalid" in str(error.value)
        resolve_app_data_mock.assert_called_once_with(File.GDriveToken)
        delete_file_mock.assert_called_once()


    def test_game_config_properties(self, _games_config):
        """
        Tests basic properties: list, names, empty, by_name, current.
        """

        from savegem.common.core.game_config import Game, GameSettings

        # Initial state
        assert _games_config.empty is True

        _games_config.initialize()
        first_game = _games_config.by_name(_games_config.names[0])

        assert len(_games_config) == 2
        assert isinstance(first_game, Game)
        assert isinstance(first_game.settings, GameSettings)
        assert _games_config.names == [GameTestData.FirstGame, "Game D (No Filter)"]

        game_a = _games_config.by_name(GameTestData.FirstGame)
        assert game_a.process_name == "GameA.exe"
        assert game_a.logo == "/resource/path/Game 1.jpg"
        assert _games_config.current.name == GameTestData.FirstGame
        assert _games_config.empty is False


    def test_game_config_refresh_calls_game_meta_refresh(self, mocker: MockerFixture, _games_config):
        """
        Verifies that refresh() calls refresh on LocalMetadata for each game.
        """

        from savegem.common.core.save_meta import LocalMetadata

        # Mock the LocalMetadata.refresh method which is called via game.meta.local.refresh()
        mock_local_refresh = mocker.patch.object(LocalMetadata, "refresh")

        _games_config.initialize()
        _games_config.refresh()

        # We expect 2 calls, one for Game A and one for Game D
        assert mock_local_refresh.call_count == 2


class TestGameSettings(GameModuleTestHelper):

    def test_game_settings_on_init_loads_existing_data(self, games_config_mock, user_config_mock, _game, db_mock,
                                                       db_table_mock):
        from savegem.common.core.game_config import GameSettings

        user_config_mock.current.id = "test_user"
        db_table_mock.reset_mock()
        # Simulate scenario where settings are already in database.
        db_table_mock.rows = [1]

        GameSettings(_game, games_config_mock)

        db_table_mock.where.assert_called_with("user_id = ? AND game_name = ?", "test_user", _game.name)
        db_table_mock.retrieve.assert_called_once()

        db_table_mock.set.assert_not_called()
        db_table_mock.save.assert_not_called()

    def test_game_settings_on_init_creates_if_no_data(self, games_config_mock, user_config_mock, _game, db_mock,
                                                      db_table_mock):
        from savegem.common.core.game_config import GameSettings

        user_config_mock.current.id = "test_user"
        db_table_mock.reset_mock()
        # Simulate scenario where settings are already in database.
        db_table_mock.rows = []

        GameSettings(_game, games_config_mock)

        db_table_mock.where.assert_called_with("user_id = ? AND game_name = ?", "test_user", _game.name)
        db_table_mock.retrieve.assert_called_once()

        assert db_table_mock.add_row.call_count == 1
        assert db_table_mock.set.call_count == 2
        assert db_table_mock.save.call_count == 1

    def test_auto_mode_setting(self, db_table_mock, games_config_mock, _game):
        from savegem.common.core.game_config import GameSettings

        db_table_mock.get_first.return_value = 1
        settings = GameSettings(_game, games_config_mock)
        db_table_mock.save.reset_mock()

        assert settings.auto_mode == 1
        db_table_mock.get_first.assert_called_once_with("auto_mode_enabled")
        db_table_mock.save.assert_not_called()

        settings.auto_mode = False
        db_table_mock.set_first.assert_called_once_with("auto_mode_enabled", 0)
        db_table_mock.save.assert_called_once()

    def test_reload(self, db_table_mock, games_config_mock, _game):
        from savegem.common.core.game_config import GameSettings

        settings = GameSettings(_game, games_config_mock)
        db_table_mock.retrieve.reset_mock()

        settings.reload()

        db_table_mock.retrieve.assert_called_once()


class TestGame(GameModuleTestHelper):

    def test_game_properties(self, _game):
        """
        Tests basic Game properties.
        """

        assert _game.name == "Test Game"
        assert _game.process_name == "Test.exe"
        assert _game.drive_directory == "test_drive_id"
        assert _game.auto_mode_allowed is True
        assert _game.players == [PlayerTestData.FirstPlayerEmail]

    def test_game_local_path_expands_vars(self, module_patch, _game, _game_path):
        """
        Verifies local_path uses os.path.expandvars.
        """

        mock_expandvars = module_patch(
            "os.path.expandvars",
            return_value="/user/home/TestSaves"
        )

        assert _game.local_path == "/user/home/TestSaves"
        mock_expandvars.assert_called_once_with(_game_path)

    def test_game_metadata_file_path(self, _game, module_patch):
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

    def test_game_filter_patterns_with_filter(self, _game):
        """
        Tests filter_patterns when filters are defined.
        """

        patterns = _game.filter_patterns

        assert len(patterns) == 3
        assert patterns[0].pattern == "save.*\\.dat"
        assert patterns[1].pattern == "save.*\\.bak"
        assert patterns[2].pattern == "service_info\\.ini"

        assert patterns[0].match("save001.dat") is not None
        assert patterns[0].match("service_info.ini") is None

    def test_game_filter_patterns_no_filter(self, _games_config, _game_path):
        """
        Tests filter_patterns when the filter list is empty (should default to ".*").
        """

        from savegem.common.core.game_config import Game

        # Arrange: Create a Game instance with an empty filter list
        game_no_filter = Game(
            game_config=_games_config,
            name="NoFilter",
            process_name="N/A",
            logo="test",
            local_path=_game_path,
            drive_directory="N/A",
            files_filter=[],  # Empty list
            auto_mode_allowed=True,
            players=[PlayerTestData.FirstPlayerEmail]
        )

        patterns = game_no_filter.filter_patterns

        assert len(patterns) == 1
        # Should default to matching all files (.*)
        assert patterns[0].pattern == ".*"
        assert patterns[0].match("anyfile.txt") is not None

    def test_game_file_list_filtering(self, _game, path_join_mock, listdir_mock, expandvars_mock):
        """
        Tests file_list property, ensuring files are filtered by regex.
        """

        expandvars_mock.return_value = "/user/home/TestSaves"
        listdir_mock.return_value = [
            "save_100.dat",  # Matches pattern 1
            "service_info.ini",  # Matches pattern 2
            "temp.log",  # No match
            "save_001.bak",  # Matches pattern 1
            "metadata_file.json",  # No match
        ]

        # 2. Act: Convert the generator to a list
        file_list = list(_game.file_list)

        # 3. Assert: Only expected files should be included, and they should be sorted
        assert file_list == [
            "/user/home/TestSaves/service_info.ini",
            "/user/home/TestSaves/save_001.bak",
            "/user/home/TestSaves/save_100.dat"
        ]

        listdir_mock.assert_called_once_with("/user/home/TestSaves")
        # Verify join was called for each included file
        assert path_join_mock.call_count == 3

