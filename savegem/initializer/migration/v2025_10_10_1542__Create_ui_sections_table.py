from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_10_1542__Create_ui_sections_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        # Create ui_sections table.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ui_sections (
                section_id VARCHAR PRIMARY KEY,
                section_label VARCHAR NOT NULL,
                section_icon VARCHAR,
                controller VARCHAR,
                order_id INTEGER NOT NULL
            )
        """)
