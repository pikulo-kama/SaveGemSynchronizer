
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_11_04_1612__Create_setup_font_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_font (
                font_id     VARCHAR PRIMARY KEY,
                font_size   INTEGER,
                font_family VARCHAR,
                font_weight INTEGER DEFAULT 400
            )
        """)
