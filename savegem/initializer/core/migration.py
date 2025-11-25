from sqlite3 import Connection

from savegem.common.db.manager import DatabaseManager
from savegem.common.util.logger import get_logger
from savegem.initializer.core.table import TableDDL


_logger = get_logger(__name__)


class Migration:
    """
    Python SQL migration wrapper.
    """

    def migrate(self, manager: DatabaseManager):
        """
        Used to migrate migration and apply changes
        in database.

        Will roll back all migration changes if there
        is an exception during execution.
        """

        connection = manager.connection()

        try:
            self._migrate(connection)
            connection.commit()

        except Exception as error:  # noqa
            _logger.error("Error running migration %s: %s", self.__class__.__name__, error)
            connection.rollback()
            raise error

    def _migrate(self, connection: Connection):
        """
        Should be implemented by migrations.
        Should include actual schema changes.
        """
        pass

    def add_foreign_key(self, connection: Connection,  # noqa
                        table_name: str, ref_table_name: str,
                        from_cols: list[str], to_cols: list[str],
                        on_delete: str = "NO ACTION",
                        on_update: str = "NO ACTION"):
        """
        Used to add foreign key to existing table.
        Since sqlite is kind of stupid and doesn't allow to
        add foreign key to existing table, we do the following:

        - Using table metadata from database recreate DDL of the table.
        - Rename original table.
        - Create new table using generated DDL.
        - Move data from original table to the new one.
        - Remove original table.
        """

        # Need to collect table DDL before table gets renamed.
        table_ddl = TableDDL(connection, table_name)
        table_ddl.add_foreign_key(from_cols, ref_table_name, to_cols, on_delete, on_update)
        cursor = connection.cursor()

        cursor.execute("PRAGMA foreign_keys = OFF")

        # Rename existing table.
        old_table_name = f"{table_name}_old"
        cursor.execute(f"ALTER TABLE {table_name} RENAME TO {old_table_name}")

        # Create new table with foreign key.
        cursor.execute(table_ddl.build())

        # Copy data to new table.
        cursor.execute(f"""
            INSERT INTO {table_name} 
            SELECT * FROM {old_table_name}
        """)

        # Remove old table.
        cursor.execute(f"DROP TABLE {old_table_name}")

        cursor.execute("PRAGMA foreign_keys = ON")
