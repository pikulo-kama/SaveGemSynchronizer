from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_10_0233__Create_state_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                user_id         VARCHAR PRIMARY KEY,
                language        VARCHAR,
                current_game    VARCHAR,
                time_format_id  INTEGER,
                window_width    INTEGER,
                window_height   INTEGER
            )
        """)
