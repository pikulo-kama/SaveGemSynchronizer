import sqlite3
from typing import Optional, Final

from savegem.common.db.table import DatabaseTable
from savegem.common.util.file import resolve_app_data
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)
_db: Optional["DatabaseManager"] = None


def db():
    """
    Used to get global instance
    of database manager.
    """

    global _db

    if _db is None:
        _db = DatabaseManager()

    return _db


class DatabaseManager:
    """
    Wrapper for sqlite connection.
    Used for low level database interactions.
    """

    DatabaseName: Final = "savegem.db"

    def retrieve_table(self, table_name: str) -> DatabaseTable:
        """
        Used to create table object to perform
        CRUD operations on table data.

        Will automatically retrieve all table data.
        """
        return self.table(table_name).retrieve()

    def table(self, table_name: str) -> DatabaseTable:
        """
        Used to create table object to perform
        CRUD operations on table data.
        """
        return DatabaseTable(self, table_name)

    def execute(self, sql: str, *args, **kwargs):
        """
        Used to execute edit statements.
        """

        _logger.debug("Executing alter statement.")
        _logger.debug("SQL: %s", sql)
        _logger.debug("args=%s, kw=%s", args, kwargs)

        connection = self.connection()
        connection.execute(sql, *args, **kwargs)  # noqa
        connection.commit()

    def select(self, sql: str, *args, **kwargs):
        """
        Used to execute select statements.
        """

        _logger.debug("Executing select statement.")
        _logger.debug("SQL: %s", sql)
        _logger.debug("args=%s, kw=%s", args, kwargs)

        connection = self.connection()
        cursor = connection.cursor()
        cursor.execute(sql, *args, **kwargs)  # noqa

        return cursor

    def connection(self):
        """
        Used to create sqlite connection.
        """
        return sqlite3.connect(resolve_app_data(self.DatabaseName))
