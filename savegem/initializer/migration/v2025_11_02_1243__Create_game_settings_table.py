
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_02_1243__Create_game_settings_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS game_settings (
                game_name VARCHAR PRIMARY KEY,
                auto_mode_enabled INTEGER
            )
        """)
