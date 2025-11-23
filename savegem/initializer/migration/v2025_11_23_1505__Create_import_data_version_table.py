
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_23_1505__Create_import_data_version_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS import_data_version (
                file_name   VARCHAR PRIMARY KEY,
                checksum    VARCHAR
            )
        """)
