
from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_23_1308__Create_text_resource_table(Migration):  # noqa

    def _migrate(self, connection: Connection):

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_locale (
                locale_id VARCHAR PRIMARY KEY,
                locale_name VARCHAR NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS setup_text_resource (
                text_resource_key VARCHAR NOT NULL,
                locale_id VARCHAR NOT NULL,
                text_resource VARCHAR,
                
                PRIMARY KEY (text_resource_key, locale_id),
                FOREIGN KEY (locale_id) REFERENCES setup_locale(locale_id)
            )
        """)
