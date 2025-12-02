from tests.test_data import PlayerTestData


class TestUserResolver:

    def test_should_handle_not_supported_args(self):

        from savegem.app.gui.widget.resolver.user import UserResolver

        resolver = UserResolver()
        assert resolver.resolve("test1") == ""
        assert resolver.resolve("nonExisting2") == ""

    def test_should_return_current_game_name(self, user_config_mock):

        from savegem.app.gui.widget.resolver.user import UserResolver

        resolver = UserResolver()
        assert resolver.resolve("name") == PlayerTestData.FirstPlayerName

    def test_should_return_current_user_photo(self, user_config_mock):

        from savegem.app.gui.widget.resolver.user import UserResolver

        resolver = UserResolver()
        assert resolver.resolve("photo") == PlayerTestData.ProfilePictureUrl
