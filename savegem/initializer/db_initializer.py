import datetime

from savegem.common.db.manager import db, DatabaseManager
from savegem.initializer.core.migration import Migration
from savegem.initializer.migration import get_migrations


class DatabaseInitializer:
    """
    Used to initialize and migrate database.
    """

    @classmethod
    def run(cls, _):
        cls.__initialize()
        cls.__migrate()

    @staticmethod
    def __initialize():
        """
        Used to create schema version table.
        Table is used to keep track of what
        migrations have been already executed.
        """

        db().execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY,
                file_name VARCHAR,
                version VARCHAR,
                description VARCHAR,
                date_applied VARCHAR,
                success INTEGER
            )
        """)

    @classmethod
    def __migrate(cls):
        """
        Used to execute all migrations that haven't
        been executed yet.

        Will also update schema_version table for
        all new migrations that have been executed.
        """

        manager = db()

        migrations = list(get_migrations())
        last_migration_name, _ = migrations[-1]

        if cls.__migration_exists(manager, last_migration_name):
            return

        for member_name, member in migrations:

            if cls.__migration_exists(manager, member_name):
                continue

            migration: Migration = member()
            migration.migrate(manager)

            cls.__update_schema_version(manager, member_name)

    @classmethod
    def __migration_exists(cls, manager: DatabaseManager, migration_name: str):
        """
        Used to check whether migration with provided name already exists.
        """

        cursor = manager.select("SELECT 1 FROM schema_version WHERE file_name = ?", (migration_name,))
        return cursor.fetchone() is not None

    @classmethod
    def __update_schema_version(cls, manager: DatabaseManager, migration_name: str):
        """
        Used to add migration to schema_version table.
        """

        parts = migration_name.split("__")

        if len(parts) != 2:
            raise RuntimeError(f"Migration %s is invalid.", migration_name)

        version, description = parts
        version = version.replace("v", "").replace("_", ".")
        description = description.replace("_", " ")

        manager.execute(f"""
            INSERT INTO schema_version (file_name, version, description, date_applied, success)
            VALUES (?, ?, ?, ?, ?)
        """, (migration_name, version, description, datetime.datetime.now(), 1))
