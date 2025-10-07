import pytest
from pytest_mock import MockerFixture

from tests.test_data import LocaleTestData


@pytest.fixture(autouse=True)
def _setup(mocker: MockerFixture, json_config_holder_mock, resolve_locale_mock):

    from savegem.common.core.text_resource import TextResource
    from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder

    # Reset text resource state.
    mocker.patch.object(TextResource, "_TextResource__current_locale", None)
    mocker.patch.object(TextResource, "_TextResource__holder", None)

    first_locales_holder = MockJsonConfigHolder({
        "key1": LocaleTestData.FirstLocale,
        "key2": f"{LocaleTestData.FirstLocale},{{0}},{{1}}",
    })

    second_locales_holder = MockJsonConfigHolder({
        "key1": LocaleTestData.SecondLocale,
        "key2": f"{LocaleTestData.SecondLocale},{{0}},{{1}}",
    })

    resolve_locale_mock.side_effect = lambda path: path
    json_config_holder_mock.side_effect = lambda locale: first_locales_holder \
        if locale == LocaleTestData.FirstLocale \
        else second_locales_holder


def test_should_not_read_file_again_if_locale_same(json_config_holder_mock):

    from savegem.common.core.text_resource import TextResource

    TextResource.get(LocaleTestData.FirstLocale, "key1")
    TextResource.get(LocaleTestData.FirstLocale, "key1")

    json_config_holder_mock.assert_called_once()


def test_should_read_file_if_locale_changed(json_config_holder_mock):

    from savegem.common.core.text_resource import TextResource

    TextResource.get(LocaleTestData.FirstLocale, "key1")
    TextResource.get(LocaleTestData.SecondLocale, "key1")

    assert json_config_holder_mock.call_count == 2


def test_should_handle_non_existing_keys():

    from savegem.common.core.text_resource import TextResource

    non_existing_key = "key321"
    value = TextResource.get(LocaleTestData.FirstLocale, non_existing_key, "arg1", "arg2")

    assert value == non_existing_key


def test_should_resolve_arguments():

    from savegem.common.core.text_resource import TextResource

    value = TextResource.get(LocaleTestData.FirstLocale, "key2", "arg1", "arg2")
    assert value == f"{LocaleTestData.FirstLocale},arg1,arg2"


def test_tr_should_use_local_from_state(app_state_mock):

    from savegem.common.core.text_resource import tr

    app_state_mock.locale = LocaleTestData.FirstLocale
    assert tr("key1") == LocaleTestData.FirstLocale

    app_state_mock.locale = LocaleTestData.SecondLocale
    assert tr("key1") == LocaleTestData.SecondLocale
