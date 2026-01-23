

class TestApplicationContext:

    def test_property_accessors(self, module_patch):
        """
        Tests that all public properties return the correct, cached mock instance.
        """

        from src.savegem.common.core.context import ApplicationContext

        user_state = module_patch("UserState")
        app_state = module_patch("AppState")
        app_config = module_patch("AppConfig")
        game_config = module_patch("GameConfig")
        activity = module_patch("Activity")

        context = ApplicationContext()

        assert context.users is user_state.return_value
        assert context.state is app_state.return_value
        assert context.config is app_config.return_value
        assert context.games is game_config.return_value
        assert context.activity is activity.return_value
