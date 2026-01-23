from tests.test_data import GameTestData


class TestGameResolver:

    def test_should_handle_not_supported_args(self):

        from src.savegem import GameResolver

        resolver = GameResolver()
        assert resolver.resolve("test1") == ""
        assert resolver.resolve("nonExisting2") == ""

    def test_should_return_current_game_name(self, games_config_mock):

        from src.savegem import GameResolver

        resolver = GameResolver()
        assert resolver.resolve("name") == GameTestData.FirstGame

    def test_should_return_current_game_logo(self, games_config_mock):

        from src.savegem import GameResolver

        resolver = GameResolver()
        assert resolver.resolve("logo") == GameTestData.FirstGameLogo