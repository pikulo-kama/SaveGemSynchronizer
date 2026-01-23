from tests.test_data import ConfigTestData


class TestAppConfig:

    def test_should_return_config_properties(self, app_context_mock, json_config_holder_mock):

        from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder
        from src.savegem.common import AppConfig

        json_config_holder_mock.return_value = MockJsonConfigHolder({
            AppConfig.ActivityLogFileProp: ConfigTestData.ActivityLogFileId,
            AppConfig.GameConfigFileProp: ConfigTestData.GameConfigFileId,
            AppConfig.UsersConfigFileProp: ConfigTestData.UsersConfigFileId
        })

        config = AppConfig(app_context_mock)

        assert config.games_config_file_id == ConfigTestData.GameConfigFileId
        assert config.activity_log_file_id == ConfigTestData.ActivityLogFileId
        assert config.users_config_file_id == ConfigTestData.UsersConfigFileId
