
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_22_2245__Create_setup_resource_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_resource (
                resource_name VARCHAR PRIMARY KEY,
                resource_path VARCHAR NOT NULL,
                color VARCHAR
            )
        """)
