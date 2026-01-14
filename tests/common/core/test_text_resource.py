import pytest
from pytest_mock import MockerFixture

from tests.test_data import LocaleTestData


class TestTextResource:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture, db_table_mock):

        from savegem.common.core.text_resource import TextResource
        from savegem.common.db.table import DatabaseRow

        # Reset text resources state.
        mocker.patch.object(TextResource, "_TextResource__current_locale", None)
        mocker.patch.object(TextResource, "_TextResource__resource_map", {})

        def remember_locale(_, locale_id):
            db_table_mock.selected_locale = locale_id
            return db_table_mock

        table_columns = ["text_resource_key", "text_resource"]
        db_table_mock.where.side_effect = remember_locale

        first_locale_data = [
            DatabaseRow(1, ("key1", LocaleTestData.FirstLocale), table_columns),
            DatabaseRow(2, ("key2", f"{LocaleTestData.FirstLocale},{{0}},{{1}}"), table_columns)
        ]

        second_locale_data = [
            DatabaseRow(1, ("key1", LocaleTestData.SecondLocale), table_columns),
            DatabaseRow(2, ("key2", f"{LocaleTestData.SecondLocale},{{0}},{{1}}"), table_columns)
        ]

        def get_locales():
            if db_table_mock.selected_locale == LocaleTestData.FirstLocale:
                return iter(first_locale_data)
            else:
                return iter(second_locale_data)

        db_table_mock.__iter__.side_effect = get_locales


    def test_should_not_read_file_again_if_locale_same(self, db_mock):

        from savegem.common.core.text_resource import TextResource

        TextResource.get(LocaleTestData.FirstLocale, "key1")
        TextResource.get(LocaleTestData.FirstLocale, "key1")

        db_mock.table.assert_called_once()


    def test_reset(self, db_mock):

        from savegem.common.core.text_resource import TextResource

        TextResource.get(LocaleTestData.FirstLocale, "key1")
        TextResource.reset()
        TextResource.get(LocaleTestData.FirstLocale, "key1")

        assert db_mock.table.call_count == 2


    def test_should_read_file_if_locale_changed(self, db_mock):

        from savegem.common.core.text_resource import TextResource

        TextResource.get(LocaleTestData.FirstLocale, "key1")
        TextResource.get(LocaleTestData.SecondLocale, "key1")

        assert db_mock.table.call_count == 2


    def test_should_handle_non_existing_keys(self):

        from savegem.common.core.text_resource import TextResource

        non_existing_key = "key321"
        value = TextResource.get(LocaleTestData.FirstLocale, non_existing_key, "arg1", "arg2")

        assert value == non_existing_key


    def test_should_resolve_arguments(self):

        from savegem.common.core.text_resource import TextResource

        value = TextResource.get(LocaleTestData.FirstLocale, "key2", "arg1", "arg2")
        assert value == f"{LocaleTestData.FirstLocale},arg1,arg2"


    def test_tr_should_use_local_from_state(self, app_state_mock):

        from savegem.common.core.text_resource import tr

        app_state_mock.locale = LocaleTestData.FirstLocale
        assert tr("key1") == LocaleTestData.FirstLocale

        app_state_mock.locale = LocaleTestData.SecondLocale
        assert tr("key1") == LocaleTestData.SecondLocale
