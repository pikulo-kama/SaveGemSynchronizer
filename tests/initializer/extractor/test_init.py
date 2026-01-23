import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


class TestRegularExtractor:

    @pytest.fixture
    def _custom_extractor_mock(self):
        from src.savegem import RegularExtractor

        class MockCustomExtractor(RegularExtractor):
            """
            A mock custom extractor used for testing dynamic loading.
            """

            def do_extract(self, args):
                # Simply record that this was called
                self.extracted_data = True

            def __init__(self):
                super().__init__()
                self.extracted_data = False

        return MockCustomExtractor


    @pytest.fixture
    def mock_args(self, mocker: MockerFixture):
        """
        Fixture to provide a mock argparse Namespace object.
        """

        from src.savegem import RegularExtractorName

        args = mocker.MagicMock()
        args.type = RegularExtractorName
        args.table_name = "test_table"
        args.output = "test_output_dir"
        args.filter = None

        return args


    @pytest.fixture
    def mock_db_interaction(self, mocker):
        """
        Mocks the database manager, table, and row retrieval.
        """

        # 1. Mock Row objects with a to_json method
        mock_row1 = MagicMock()
        mock_row1.to_json.return_value = {"id": 1, "name": "Alice", "value": None}
        mock_row2 = MagicMock()
        mock_row2.to_json.return_value = {"id": 2, "name": "Bob", "value": 42}

        # 2. Mock the retrieve method to return the rows
        mock_table = MagicMock()
        mock_table.retrieve.return_value = [mock_row1, mock_row2]

        # 3. Mock the where method (chaining)
        mock_table.where.return_value = mock_table

        # 4. Mock db() and db().table()
        mock_db = MagicMock()
        mock_db.table.return_value = mock_table
        mocker.patch('your_module.initializer.extractor.db', return_value=mock_db)

        return mock_db, mock_table


    @pytest.fixture
    def _datetime_now(self):
        return datetime.datetime(2025, 11, 27, 10, 0, 0)


    @pytest.fixture(autouse=True)
    def mock_file_and_os(self, save_file_mock, path_join_mock, datetime_mock, _datetime_now):
        """
        Mocks file system operations and datetime for consistency.
        """

        path_join_mock.return_value = "/mock/root/test_output_dir/test_table.json"
        datetime_mock.now.return_value = _datetime_now


    def test_get_extractors_filters_correctly(self, _custom_extractor_mock, get_members_mock):
        """
        Tests that get_extractors correctly uses get_members to find
        subclasses of RegularExtractor (excluding RegularExtractor itself).
        """

        from src.savegem import RegularExtractor
        from src.savegem import get_extractors

        # Mock the reflection utility to return test members
        get_members_mock.return_value = [
            ("RegularExtractor", RegularExtractor),
            ("CustomExtractor", _custom_extractor_mock)
        ]

        # The return list should not contain RegularExtractor
        extractors = get_extractors()

        assert len(extractors) == 2
        assert extractors[0][0] == "RegularExtractor"
        assert extractors[1][0] == "CustomExtractor"
        assert extractors[0][1] == RegularExtractor
        assert extractors[1][1] == _custom_extractor_mock


    def test_invoke_extractor_uses_regular_by_default(self, mocker: MockerFixture, mock_args):
        """
        Tests that if the type is Regular, RegularExtractor.do_extract is called.
        """

        from src.savegem import invoke_extractor, RegularExtractor

        # Mock the RegularExtractor instance method
        mock_do_extract = mocker.patch.object(RegularExtractor, 'do_extract')
        invoke_extractor(mock_args)

        # Should create a RegularExtractor and call its do_extract method
        mock_do_extract.assert_called_once_with(mock_args)


    def test_invoke_extractor_dispatches_to_custom_extractor(self, mocker: MockerFixture, module_patch, mock_args,
                                                             _custom_extractor_mock):
        """
        Tests that a custom extractor is correctly identified and invoked.
        """

        from src.savegem import invoke_extractor, RegularExtractor

        mock_args.type = "Custom"
        custom_instance = _custom_extractor_mock()

        module_patch("get_extractors").return_value = [("CustomExtractor", lambda: custom_instance)]
        mock_do_extract = mocker.patch.object(custom_instance, 'do_extract')

        invoke_extractor(mock_args)

        mock_do_extract.assert_called_once_with(mock_args)
        mocker.patch.object(RegularExtractor, 'do_extract').assert_not_called()


    def test_regular_extractor_calls_db_and_saves_file(self, mock_args, db_mock, db_table_mock, save_file_mock,
                                                       path_mock, _datetime_now):
        """
        Tests the main success path of do_extract without filtering.
        """

        from src.savegem import RegularExtractor
        from src.savegem import DatabaseRow

        db_table_mock.retrieve.return_value = [
            DatabaseRow(1, (1, "Alice", None), ["id", "name", "value"]),
            DatabaseRow(1, (2, "Bob", 42), ["id", "name", "value"]),
        ]

        extractor = RegularExtractor()
        extractor.do_extract(mock_args)

        # 1. DB interaction check
        db_mock.table.assert_called_once_with("test_table")
        db_table_mock.retrieve.assert_called_once()
        db_table_mock.where.assert_not_called()

        # 2. File system checks
        path_mock.return_value.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

        expected_content = {
            "metadata": {
                "table_name": "test_table",
                "type": "Regular",
                "extract_date": _datetime_now.isoformat()
            },
            "data": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob", "value": 42}
            ]
        }

        save_file_mock.assert_called_once_with(
            str(path_mock.return_value),
            expected_content,
            as_json=True
        )


    def test_regular_extractor_applies_filter(self, mock_args, db_mock, db_table_mock, save_file_mock):
        """
        Tests that a filter argument correctly invokes table.where() and adds filter to metadata.
        """

        from src.savegem import RegularExtractor

        mock_args.filter = "column > 10"

        extractor = RegularExtractor()
        extractor.do_extract(mock_args)

        # 1. DB interaction check
        db_table_mock.where.assert_called_once_with("column > 10")

        # 2. Metadata check (requires inspecting the save_file call)
        saved_content = save_file_mock.call_args[0][1]
        assert saved_content["metadata"]["filter"] == "column > 10"


    def test_regular_extractor_calls_post_extract(self, mocker, mock_args, save_file_mock, db_mock, db_table_mock):
        """
        Tests that the _post_extract method is correctly called with processed data.
        """

        from src.savegem import RegularExtractor
        from src.savegem import DatabaseRow

        # Mock _post_extract to change the data structure
        mock_post_extract = mocker.patch.object(RegularExtractor, '_post_extract', return_value=["Modified Data"])
        db_table_mock.retrieve.return_value = [
            DatabaseRow(1, (1, "Alice", None), ["id", "name", "value"]),
            DatabaseRow(1, (2, "Bob", 42), ["id", "name", "value"]),
        ]

        extractor = RegularExtractor()
        extractor.do_extract(mock_args)

        expected_input_to_post_extract = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob", "value": 42}
        ]
        mock_post_extract.assert_called_once()
        # Need to check the content of the argument, which is a deep copy
        assert mock_post_extract.call_args[0][0] == expected_input_to_post_extract

        # 2. Check the saved file content used the return value from _post_extract
        saved_content = save_file_mock.call_args[0][1]
        assert saved_content["data"] == ["Modified Data"]
