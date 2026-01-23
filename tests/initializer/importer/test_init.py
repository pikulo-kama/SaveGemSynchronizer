from pytest_mock import MockerFixture
from unittest.mock import call
import pytest


class TestRegularImporter:

    @pytest.fixture
    def _custom_importer_mock(self):
        from src.savegem import RegularImporter

        class MockCustomImporter(RegularImporter):
            """
            A mock custom importer used for testing dynamic loading.
            """

            def do_import(self, args):
                self.imported_data = True

            def __init__(self):
                super().__init__()
                self.imported_data = False

        return MockCustomImporter


    @pytest.fixture
    def _invoke_file_mock(self, module_patch):
        return module_patch("invoke_importer_for_file")


    @pytest.fixture
    def _mock_args(self, mocker: MockerFixture):
        args = mocker.MagicMock()
        args.file_name = None
        args.definition_file = "test.def"

        return args


    @pytest.fixture
    def _custom_importers(self, get_members_mock, _custom_importer_mock):

        from src.savegem import RegularImporter

        importers = [
            ("RegularImporter", RegularImporter),
            ("CustomImporter", _custom_importer_mock)
        ]

        get_members_mock.return_value = importers
        return dict(importers)


    # Fixture for mocking the UI IPC
    @pytest.fixture(autouse=True)
    def _mock_ui_socket(self, module_patch):
        return module_patch("ui_socket")


    def test_invoke_importer_for_file_dispatches_regular(self, mocker, _mock_args, read_file_mock, _custom_importers):
        """
        Verifies default RegularImporter is called.
        """

        from src.savegem import RegularImporter
        from src.savegem import invoke_importer_for_file

        _mock_args.file_name = "test.json"
        read_file_mock.return_value = {"metadata": {"type": "Regular"}, "data": []}
        mock_do_import = mocker.patch.object(RegularImporter, 'do_import')

        invoke_importer_for_file(_mock_args.file_name, _custom_importers, _mock_args)

        mock_do_import.assert_called_once()
        assert _mock_args.file_name == "test.json"


    def test_invoke_importer_for_file_dispatches_custom(self, mocker, _mock_args, read_file_mock, _custom_importer_mock,
                                                        _custom_importers):
        """
        Verifies dynamic dispatch to CustomImporter.
        """

        from src.savegem import RegularImporter
        from src.savegem import invoke_importer_for_file

        _mock_args.file_name = "custom_test.json"

        # Mock the file content to use Custom type
        read_file_mock.return_value = {"metadata": {"type": "Custom"}, "data": []}

        # Mock the custom importer's do_import
        mock_do_import = mocker.patch.object(_custom_importer_mock, 'do_import')

        invoke_importer_for_file(_mock_args.file_name, _custom_importers, _mock_args)

        # Assert CustomImporter's do_import was called, Regular's was not
        mock_do_import.assert_called_once()
        mocker.patch.object(RegularImporter, 'do_import').assert_not_called()
        assert _mock_args.file_name == "custom_test.json"


    def test_invoke_importer_with_file_name_argument(self, module_patch, read_file_mock, _mock_args, _custom_importers,
                                                     _mock_ui_socket, _invoke_file_mock):
        """
        Test flow when --file_name is provided (skips checksums).
        """

        from src.savegem import invoke_importer

        _mock_args.file_name = "direct_file.json"
        invoke_importer(_mock_args)

        _invoke_file_mock.assert_called_once_with("direct_file.json", _custom_importers, _mock_args)
        read_file_mock.assert_not_called()
        _mock_ui_socket.send.assert_not_called()


    @pytest.mark.parametrize("is_empty, set_first_call_count", [
        (False, 2),
        (True, 4)
    ])
    def test_invoke_importer_with_definition_file_imports_new_files(self, mocker, _mock_args, db_table_mock,
                                                                    read_file_mock, file_checksum_mock, _mock_ui_socket,
                                                                    _invoke_file_mock, is_empty, set_first_call_count):
        """
        Test flow when --definition_file is provided and checksums differ.
        """

        from src.savegem import invoke_importer

        # Definition file content (two files, one comment, one empty line)
        read_file_mock.side_effect = [
            "file1.json\n# Comment\nfile2.json\n",
            {"metadata": {"type": "Regular"}, "data": []}
        ]
        file_checksum_mock.side_effect = ["45678", "98765"]

        # Configure DB metadata for file1 (new entry) and file2 (old checksum)
        # File1: metadata is_empty=True (default) -> Forces insertion and import
        # File2: metadata is_empty=False, current_checksum="12345" -> Forces update and import
        db_table_mock.is_empty = is_empty
        db_table_mock.get_first.side_effect = [
            None, "12345"
        ]

        invoke_importer(_mock_args)

        # Check if both files were imported because the checksums were different
        expected_file_calls = [
            call('file1.json', mocker.ANY, _mock_args),
            call('file2.json', mocker.ANY, _mock_args)
        ]

        _invoke_file_mock.assert_has_calls(expected_file_calls, any_order=False)
        assert _invoke_file_mock.call_count == 2

        # Check that metadata was updated and saved for both files
        assert db_table_mock.set_first.call_count == set_first_call_count
        assert db_table_mock.save.call_count == 2  # Called once per file

        _mock_ui_socket.send.assert_called_once()  # UI command sent at the end


    def test_invoke_importer_with_definition_file_skips_unchanged_files(self, db_table_mock, _mock_args,
                                                                        _invoke_file_mock, read_file_mock,
                                                                        file_checksum_mock):
        """
        Test flow when checksums match, skipping import.
        """

        from src.savegem import invoke_importer

        # Definition file contains one file
        read_file_mock.return_value = "file_unchanged.json\n"

        # Ensure checksums match
        file_checksum_mock.return_value = "SAME_CHECKSUM"
        db_table_mock.is_empty = False
        db_table_mock.get_first.return_value = "SAME_CHECKSUM"

        invoke_importer(_mock_args)

        _invoke_file_mock.assert_not_called()
        assert db_table_mock.set_first.call_count == 0  # No update needed
        assert db_table_mock.save.call_count == 1  # Still saves the metadata (even if unchanged)


    def test_regular_importer_exits_on_missing_file_name(self, _mock_args, db_mock, read_file_mock):
        """
        Tests the critical exit path when file_name is missing.
        """

        from src.savegem import RegularImporter

        _mock_args.file_name = None

        importer = RegularImporter()

        with pytest.raises(SystemExit):
            importer.do_import(_mock_args)

        db_mock.assert_not_called()
        read_file_mock.assert_not_called()


    def test_regular_importer_performs_truncate_and_insert(self, _mock_args, read_file_mock, db_table_mock, db_mock):
        """
        Tests the successful data import, checking for remove_all and add_row/set.
        """

        from src.savegem import RegularImporter

        _mock_args.file_name = "data.json"

        import_data = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"}
        ]

        # Mock the input file
        read_file_mock.return_value = {
            "metadata": {"type": "Regular", "table_name": "users", "filter": None},
            "data": import_data
        }

        # Configure add_row to return row numbers
        db_table_mock.add_row.side_effect = [1, 2]

        importer = RegularImporter()
        importer.do_import(_mock_args)

        # 1. Table selection and filter check
        db_mock.table.assert_called_once_with("users")
        db_table_mock.where.assert_not_called()

        # 2. Deletion/Truncate check
        db_table_mock.retrieve.assert_called_once()
        db_table_mock.remove_all.assert_called_once()

        # 3. Data insertion check
        expected_set_calls = [
            # Row 1 (index 0)
            call(1, 'id', 1),
            call(1, 'name', 'A'),
            # Row 2 (index 1)
            call(2, 'id', 2),
            call(2, 'name', 'B')
        ]
        db_table_mock.set.assert_has_calls(expected_set_calls, any_order=True)
        assert db_table_mock.add_row.call_count == 2

        # 4. Save calls (one after remove_all, one after insertion)
        assert db_table_mock.save.call_count == 2


    def test_regular_importer_applies_filter_before_remove_all(self, _mock_args, read_file_mock, db_table_mock):
        """
        Tests that a filter is applied to the table object before remove_all.
        """

        from src.savegem import RegularImporter

        _mock_args.file_name = "data.json"

        # Mock the input file with a filter
        read_file_mock.return_value = {
            "metadata": {"type": "Regular", "table_name": "users", "filter": "is_active = 0"},
            "data": [{"id": 1, "name": "A"}]
        }

        importer = RegularImporter()
        importer.do_import(_mock_args)

        # The filter should be applied via where()
        db_table_mock.where.assert_called_once_with("is_active = 0")

        # All subsequent operations (retrieve, remove_all, save) should operate on the filtered dataset.
        db_table_mock.retrieve.assert_called_once()
        db_table_mock.remove_all.assert_called_once()


    def test_regular_importer_calls_format_data(self, mocker: MockerFixture, _mock_args, read_file_mock, db_table_mock):
        """
        Tests that _format_data is called correctly.
        """

        from src.savegem import RegularImporter

        _mock_args.file_name = "data.json"

        raw_data = [{"id": 1, "name": "A"}]
        formatted_data = [{"id": 1, "name": "A", "status": "processed"}]

        read_file_mock.return_value = {
            "metadata": {"type": "Regular", "table_name": "users"},
            "data": raw_data
        }

        # Mock _format_data to return processed data
        mock_format = mocker.patch.object(RegularImporter, '_format_data', return_value=formatted_data)

        db_table_mock.add_row.return_value = 1

        importer = RegularImporter()
        importer.do_import(_mock_args)

        # Check that _format_data was called with raw data
        mock_format.assert_called_once_with(raw_data, {"type": "Regular", "table_name": "users"})

        # Check that the insertion used the formatted data
        db_table_mock.set.assert_has_calls([
            call(1, "id", 1),
            call(1, "name", "A"),
            call(1, "status", "processed"),
        ])
