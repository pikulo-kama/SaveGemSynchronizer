from kdb.manager import DatabaseManager
from kui.core.app import KamaApplication

_application = KamaApplication()
db = DatabaseManager(_application.config.get("datasource.db-path"))
