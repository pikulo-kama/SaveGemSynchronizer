import pytest
import datetime
from unittest.mock import call
from pytest_mock import MockerFixture


class TestDatabaseInitializer:

    @pytest.fixture
    def migration_exists_mock(self, mocker: MockerFixture):
        from savegem.initializer.db_initializer import DatabaseInitializer

        return mocker.patch.object(
            DatabaseInitializer,
            '_DatabaseInitializer__migration_exists'
        )


    @pytest.fixture
    def update_schema_version_mock(self, mocker: MockerFixture):
        from savegem.initializer.db_initializer import DatabaseInitializer

        return mocker.patch.object(
            DatabaseInitializer,
            '_DatabaseInitializer__update_schema_version'
        )


    def test_run_initializes_and_migrates(self, mocker, db_mock):
        """
        Tests that the main 'run' method correctly calls initialize and migrate.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        mock_initialize = mocker.patch.object(DatabaseInitializer, '_DatabaseInitializer__initialize')
        mock_migrate = mocker.patch.object(DatabaseInitializer, '_DatabaseInitializer__migrate')

        # The run method takes an arbitrary argument (_) which we ignore
        DatabaseInitializer.run(None)

        mock_initialize.assert_called_once()
        mock_migrate.assert_called_once()


    def test_initialize_creates_schema_version_table(self, db_mock):
        """
        Tests that __initialize executes the CREATE TABLE statement.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        # Access the private method directly
        DatabaseInitializer._DatabaseInitializer__initialize()  # noqa

        assert "CREATE TABLE IF NOT EXISTS schema_version" in db_mock.execute.call_args[0][0]


    @pytest.mark.parametrize("file_name, expected", [
        ("v2025_10_12_2205__Create_table.py", True),
        ("non_existent_migration.py", False)
    ])
    def test_migration_exists_checks_database(self, mocker: MockerFixture, db_mock, file_name, expected):
        """
        Tests that __migration_exists correctly queries the database.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        # Configure the cursor's fetchone based on expected outcome
        cursor = mocker.MagicMock()
        cursor.fetchone.return_value = (1,) if expected else None
        db_mock.select.return_value = cursor

        exists = DatabaseInitializer._DatabaseInitializer__migration_exists(db_mock, file_name)  # noqa

        assert exists == expected
        db_mock.select.assert_called_once_with(
            "SELECT 1 FROM schema_version WHERE file_name = ?", (file_name,)
        )


    def test_update_schema_version_inserts_correct_data(self, db_mock, datetime_mock):
        """
        Tests that __update_schema_version correctly parses the migration name
        and inserts a record into schema_version.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        # Mock datetime to control the date_applied value
        migration_name = "v2025_10_12_2205__Create_setup_tables.py"
        mock_now = datetime.datetime(2025, 11, 26, 10, 30, 0)
        datetime_mock.datetime.now.return_value = mock_now

        DatabaseInitializer._DatabaseInitializer__update_schema_version(db_mock, migration_name)  # noqa

        expected_version = "2025.10.12.2205"
        expected_description = "Create setup tables"

        sql = db_mock.execute.call_args[0][0]
        args = db_mock.execute.call_args[0][1]

        assert "INSERT INTO schema_version (file_name, version, description, date_applied, success)" in sql
        assert "VALUES (?, ?, ?, ?, ?)" in sql

        assert ('v2025_10_12_2205__Create_setup_tables', expected_version, expected_description, mock_now, 1) == args


    def test_update_schema_version_raises_on_invalid_name(self, db_mock):
        """
        Tests that __update_schema_version validates the migration name format.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        with pytest.raises(RuntimeError) as error:
            DatabaseInitializer._DatabaseInitializer__update_schema_version(db_mock, "invalid_name.py")  # noqa

        assert "Migration invalid_name is invalid." in str(error.value)
        db_mock.execute.assert_not_called()


    def test_migrate_skips_when_last_migration_exists(self, db_mock, listdir_mock, migration_exists_mock,
                                                      update_schema_version_mock):
        """
        Tests that __migrate exits early if the latest migration file is already in the schema_version table.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        listdir_mock.return_value = ["v1.py", "v2.py", "v3.py"]
        migration_exists_mock.return_value = True

        DatabaseInitializer._DatabaseInitializer__migrate()  # noqa

        # It should call __migration_exists exactly once for the last migration
        migration_exists_mock.assert_called_once_with(db_mock, "v3.py")

        # No migration scripts should be executed or updated
        db_mock.connection().executescript.assert_not_called()
        update_schema_version_mock.assert_not_called()


    def test_migrate_applies_new_migrations_and_updates_schema(self, module_patch, read_file_mock, db_mock,
                                                               listdir_mock, migration_exists_mock,
                                                               update_schema_version_mock):
        """
        Tests the core migration logic, applying new scripts and updating the schema table.
        """

        from savegem.initializer.db_initializer import DatabaseInitializer

        read_file_mock.side_effect = ["SQL for v2", "SQL for v3"]
        migrations = ["v1.py", "v2.py", "v3.py"]
        listdir_mock.return_value = migrations
        mock_connection = db_mock.connection.return_value

        # Configure __migration_exists to skip v1.py, but not v2.py or v3.py
        # call 1 (check last: v3.py) -> False
        # call 2 (v1.py) -> True (skips)
        # call 3 (v2.py) -> False (applies)
        # call 4 (v3.py) -> False (applies)
        migration_exists_mock.side_effect = [False, True, False, False]

        DatabaseInitializer._DatabaseInitializer__migrate()  # noqa

        # 1. Check existence calls (v3.py first, then loop v1, v2, v3)
        expected_exists_calls = [
            call(db_mock, "v3.py"),  # Initial check on last migration (returns False)
            call(db_mock, "v1.py"),  # Loop check 1 (returns True - skipped)
            call(db_mock, "v2.py"),  # Loop check 2 (returns False - executed)
            call(db_mock, "v3.py"),  # Loop check 3 (returns False - executed)
        ]
        migration_exists_mock.assert_has_calls(expected_exists_calls)
        assert migration_exists_mock.call_count == 4

        # 2. Check script execution (only for v2 and v3)
        expected_script_calls = [
            call("SQL for v2"),
            call("SQL for v3"),
        ]

        mock_connection.executescript.assert_has_calls(expected_script_calls)
        assert mock_connection.executescript.call_count == 2

        # 3. Check schema version updates (only for v2 and v3)
        expected_update_calls = [
            call(db_mock, "v2.py"),
            call(db_mock, "v3.py"),
        ]

        update_schema_version_mock.assert_has_calls(expected_update_calls)
        assert update_schema_version_mock.call_count == 2
