
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_12_2205__Create_setup_layout_and_widget_tables(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_widget_type (
                widget_type_id VARCHAR PRIMARY KEY,
                class_path VARCHAR NOT NULL,
                is_interactable INTEGER NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_layout_type (
                layout_type_id VARCHAR PRIMARY KEY,
                class_path VARCHAR NOT NULL
            )
        """)

        self.add_foreign_key(
            connection,
            "ui_widgets",
            "setup_widget_type",
            ["widget_type_id"],
            ["widget_type_id"],
            "CASCADE"
        )

        self.add_foreign_key(
            connection,
            "ui_widgets",
            "setup_layout_type",
            ["layout_type_id"],
            ["layout_type_id"],
            "CASCADE"
        )
