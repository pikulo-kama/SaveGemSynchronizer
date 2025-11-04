
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_04_1558__Create_setup_color_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_color (
                color_id    VARCHAR PRIMARY KEY,
                light       VARCHAR,
                dark        VARCHAR
            )
        """)
