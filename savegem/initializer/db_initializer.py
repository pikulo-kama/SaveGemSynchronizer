import datetime
import os

from constants import Directory
from savegem.common.db.manager import db, DatabaseManager
from savegem.common.util.file import read_file, resolve_migration, remove_extension_from_path
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class DatabaseInitializer:
    """
    Used to initialize and migrate database.
    """

    @classmethod
    def run(cls, _):
        _logger.info("Starting database upgrade.")
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

        migrations = os.listdir(Directory().Migrations)
        last_migration_name = migrations[-1]

        _logger.info("Latest observed migration: %s.", last_migration_name)
        if cls.__migration_exists(manager, last_migration_name):
            _logger.info("No migrations to perform. Exiting.")
            return

        for file_name in migrations:

            if cls.__migration_exists(manager, file_name):
                _logger.info("Migration %s has already been executed. Skipping.", file_name)
                continue

            _logger.info("Applying migration %s.", file_name)
            script = read_file(resolve_migration(file_name))
            db().connection().executescript(script)

            cls.__update_schema_version(manager, file_name)

        _logger.info("All migrations have been executed.")

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

        migration_name = remove_extension_from_path(migration_name)
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
