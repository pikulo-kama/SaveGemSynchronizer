import sqlite3
import pytest

from pytest_mock import MockerFixture


class TestDatabaseManager:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture):
        """
        Resets the global _db instance before each test to ensure test isolation.
        """

        # Access the global variable directly for reset
        from src import savegem as manager_module
        mocker.patch.object(manager_module, '_db', None)


    @pytest.fixture
    def _in_memory_db_manager(self):
        """
        Creates a DatabaseManager instance that uses an in-memory SQLite database
        for testing. This bypasses the need for mock_resolve_app_data for core logic.
        """

        from src.savegem import DatabaseManager

        class InMemoryDatabaseManager(DatabaseManager):
            def connection(self):
                # Override connection to use an in-memory database
                if not hasattr(self, '_in_memory_conn'):
                    self._in_memory_conn = sqlite3.connect(':memory:')  # noqa
                    self._in_memory_conn.execute(
                        "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
                    self._in_memory_conn.commit()

                return self._in_memory_conn

            def close(self):
                if hasattr(self, "_in_memory_conn"):
                    self._in_memory_conn.close()
                    del self._in_memory_conn

        manager = InMemoryDatabaseManager()

        yield manager

        manager.close()


    @pytest.fixture
    def _database_table_mock(self, module_patch):
        return module_patch("DatabaseTable")


    def test_db_singleton_creation(self):
        """
        Tests that the db() function creates and returns the same instance.
        """

        from src import savegem as database_module

        # Ensure it's None initially
        assert database_module._db is None

        # First call creates the instance
        manager1 = database_module.db()
        assert isinstance(manager1, database_module.DatabaseManager)

        # Second call returns the same instance
        manager2 = database_module.db()
        assert manager1 is manager2


    def test_connection_uses_resolve_app_data(self, resolve_app_data_mock):
        """
        Tests that connection() calls sqlite3.connect with the path returned
        by the mocked resolve_app_data.
        """

        from src import savegem as database_module

        resolve_app_data_mock.return_value = ":memory:"

        # Use the standard DatabaseManager, not the in-memory override,
        # to test the resolve_app_data dependency
        manager = database_module.DatabaseManager()
        conn = manager.connection()

        # Check that resolve_app_data was called correctly
        resolve_app_data_mock.assert_called_once_with(manager.DatabaseName)

        # Check that a connection object is returned
        assert isinstance(conn, sqlite3.Connection)
        conn.close()  # Clean up connection


    def test_table_returns_database_table_instance(self, module_patch, _database_table_mock, _in_memory_db_manager):
        """
        Tests that the table() method instantiates and returns a DatabaseTable object.
        """

        table_name = "test_table"
        table_instance = _in_memory_db_manager.table(table_name)

        # Check that DatabaseTable was called with the manager instance and table name
        _database_table_mock.assert_called_once_with(_in_memory_db_manager, table_name)

        # Check that the returned object is the mock instance
        assert table_instance is _database_table_mock.return_value


    def test_retrieve_table_calls_table_and_retrieve(self, _in_memory_db_manager, _database_table_mock):
        """
        Tests that retrieve_table() calls table() and then calls the retrieve()
        method on the returned DatabaseTable object.
        """

        table_name = "test_table"

        # Get the mock instance returned by DatabaseTable()
        mock_table_instance = _database_table_mock.return_value

        result = _in_memory_db_manager.retrieve_table(table_name)

        # Check that the retrieve() method was called on the mock table object
        mock_table_instance.retrieve.assert_called_once()

        # Check that the result is what the mock retrieve() method returned
        assert result is mock_table_instance.retrieve.return_value


    def test_execute_runs_sql_and_commits(self, _in_memory_db_manager):
        """
        Tests execute() with an actual edit statement on the in-memory database.
        """

        select_sql = "SELECT name FROM test_table WHERE name = ?"
        _in_memory_db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Test User",))

        # Verify the insertion by selecting the data
        cursor = _in_memory_db_manager.select(select_sql, ("Test User",))
        row = cursor.fetchone()

        assert row is not None
        assert row[0] == "Test User"

        # Test for commit by rolling back and checking if the previous change persists
        conn = _in_memory_db_manager.connection()
        conn.rollback()  # This would undo uncommitted changes

        cursor_after_rollback = _in_memory_db_manager.select(select_sql, ("Test User",))
        assert cursor_after_rollback.fetchone() is not None  # Change should still be there because execute committed


    def test_select_runs_sql_and_returns_cursor(self, _in_memory_db_manager):
        """
        Tests select() with an actual query on the in-memory database.
        """

        # Insert data first
        _in_memory_db_manager.execute("INSERT INTO test_table (name) VALUES (?)", ("Select Test",))
        cursor = _in_memory_db_manager.select("SELECT name FROM test_table WHERE name = ?", ("Select Test",))

        assert isinstance(cursor, sqlite3.Cursor)

        # Check that the data is retrieved correctly
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "Select Test"


    def test_select_with_no_results(self, _in_memory_db_manager):
        """
        Tests select() when the query returns no rows.
        """

        sql = "SELECT name FROM test_table WHERE name = ?"
        cursor = _in_memory_db_manager.select(sql, ("NonExistentName",))

        assert isinstance(cursor, sqlite3.Cursor)
        assert cursor.fetchone() is None


    def test_execute_logs_debug_info(self, _in_memory_db_manager, logger_mock):
        """
        Tests that execute() logs the correct debug information.
        """

        sql = "DELETE FROM test_table"
        _in_memory_db_manager.execute(sql)

        # Check the log calls
        # Note: Using part of the log message is usually safer than the whole string
        logger_mock.debug.assert_any_call("Executing alter statement.")
        logger_mock.debug.assert_any_call("SQL: %s", sql)
        logger_mock.debug.assert_any_call("args=%s, kw=%s", (), {})


    def test_select_logs_debug_info(self, _in_memory_db_manager, logger_mock):
        """
        Tests that select() logs the correct debug information.
        """

        sql = "SELECT * FROM test_table WHERE id = ?"
        _in_memory_db_manager.select(sql, (1,))

        # Check the log calls
        logger_mock.debug.assert_any_call("Executing select statement.")
        logger_mock.debug.assert_any_call("SQL: %s", sql)
        logger_mock.debug.assert_any_call("args=%s, kw=%s", (1,), {})
