from tests.test_data import ConfigTestData


def test_should_return_config_properties(json_config_holder_mock):

    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder
    from savegem.common.core.app_config import AppConfig

    json_config_holder_mock.return_value = MockJsonConfigHolder({
        AppConfig.ActivityLogFileProp: ConfigTestData.ActivityLogFileId,
        AppConfig.GameConfigFileProp: ConfigTestData.GameConfigFileId
    })

    config = AppConfig()

    assert config.games_config_file_id == ConfigTestData.GameConfigFileId
    assert config.activity_log_file_id == ConfigTestData.ActivityLogFileId
