import pytest
from pytest_mock import MockerFixture

from tests.test_data import LocaleTestData, SocketTestData


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture, json_config_holder_mock, resolve_config_mock):

    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder

    # Reset global module state so functions like prop() run the config loader again
    import savegem.common.core.holders as holders_module
    mocker.patch.object(holders_module, '_app_config', None)
    mocker.patch.object(holders_module, '_locales', None)

    mock_holder = MockJsonConfigHolder({
        "property": LocaleTestData.FirstLocale,
        "nested": {
            "property": SocketTestData.UIPort
        }
    })

    json_config_holder_mock.return_value = mock_holder


def test_should_read_property(json_config_holder_mock):
    from savegem.common.core.holders import prop
    assert prop("property") == LocaleTestData.FirstLocale


def test_should_read_nested_property(json_config_holder_mock):
    from savegem.common.core.holders import prop
    assert prop("nested.property") == SocketTestData.UIPort


def test_should_load_locales(listdir_mock):

    from savegem.common.core.holders import locales

    listdir_mock.return_value = [
        f"{LocaleTestData.SecondLocale}.yml",
        f"{LocaleTestData.FirstLocale}.json"
    ]

    assert locales() == [LocaleTestData.SecondLocale, LocaleTestData.FirstLocale]
