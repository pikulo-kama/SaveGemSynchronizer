
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_16_1926__Create_setup_flag_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_flag (
                flag_id     VARCHAR PRIMARY KEY,
                flag_state  INTEGER
            )
        """)
