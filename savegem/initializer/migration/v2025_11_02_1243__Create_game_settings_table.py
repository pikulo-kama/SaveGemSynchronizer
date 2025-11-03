
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_02_1243__Create_game_settings_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS game_settings (
                user_id   VARCHAR,
                game_name VARCHAR,
                auto_mode_enabled INTEGER,
                
                PRIMARY KEY (user_id, game_name)
            )
        """)
