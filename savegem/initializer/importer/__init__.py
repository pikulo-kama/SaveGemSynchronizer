import os
from typing import Any

from savegem.app.ipc_socket import ui_socket
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.db.manager import db
from savegem.common.util.file import read_file, resolve_import_data, file_checksum
from savegem.common.util.logger import get_logger
from savegem.common.util.reflection import get_members


_logger = get_logger(__name__)


def invoke_importer(args):
    """
    Used to call database importer.
    If definition file was provided will
    read import all the files listed in it.

    If file name provided directly will import
    only that file.

    Will use import data metadata to decide
    which importer implementation should be invoked.
    """

    custom_importers = dict(get_members(__package__, RegularImporter))

    # Handle scenario where import file name provided directly.
    if args.file_name is not None:
        invoke_importer_for_file(args.file_name, custom_importers, args)
        return

    definition_file: str = read_file(resolve_import_data(args.definition_file))
    files_to_import = []

    _logger.info("Importing definition file: %s", args.definition_file)

    # Handle definition_file argument.
    for line in definition_file.split("\n"):
        line = line.strip().replace("/", os.path.sep)

        # Allow comments and skip empty lines.
        if line.startswith("#") or len(line) == 0:
            continue

        actual_checksum = file_checksum(resolve_import_data(line))
        metadata = db().table("import_data_version") \
            .where("file_name = ?", line) \
            .retrieve()

        # Create entry if it doesn't exist.
        if metadata.is_empty:
            metadata.add_row()
            metadata.set_first("file_name", line)

        current_checksum = metadata.get_first("checksum")
        _logger.info("%s: current: %s, actual: %s", line, current_checksum, actual_checksum)

        # Only import data if checksum has changed.
        if current_checksum != actual_checksum:
            metadata.set_first("checksum", actual_checksum)
            files_to_import.append(line)

        else:
            _logger.info("Import file hasn't been changed. Skipping.")

        metadata.save()

    # Import files separately.
    for file_name in files_to_import:
        invoke_importer_for_file(file_name, custom_importers, args)

    ui_socket.send(IPCCommand.RebuildWindow)


def invoke_importer_for_file(file_name: str, custom_importers, args):
    """
    Used to invoke importer for provided import data file.
    """

    importer = RegularImporter()
    import_file = read_file(resolve_import_data(file_name), as_json=True)

    import_type: str = import_file.get("metadata").get("type")
    importer_name = f"{import_type}Importer"

    for member_name, member in custom_importers.items():
        if member_name == importer_name:
            importer = member()
            break

    args.file_name = file_name
    importer.do_import(args)


class RegularImporter:
    """
    Database importer.
    Allows to import data from
    JSON file to database table.

    Will remove all existing table data
    when importing.
    """

    def do_import(self, args):
        """
        Used to import data from JSON file
        into database.
        """

        if args.file_name is None:
            _logger.error("Argument '--file_name' is required for import.")
            print("Argument '--file_name' is required for import.")
            exit(1)

        import_file = read_file(resolve_import_data(args.file_name), as_json=True)
        metadata = import_file.get("metadata", {})
        table_name = metadata.get("table_name")
        filter_string = metadata.get("filter")
        data: list[dict] = import_file.get("data", [])
        data = self._format_data(data, metadata)

        _logger.info("Importing %s.", args.file_name)
        _logger.info("Importer: %s", metadata.get("type"))
        _logger.info("Table: %s", table_name)

        import_table = db().table(table_name)

        if filter_string:
            _logger.info("Filter: %s", filter_string)
            import_table.where(filter_string)

        _logger.info("-----------------")

        import_table.retrieve()

        # Remove all existing data.
        import_table.remove_all()
        import_table.save()

        for record in data:
            row_number = import_table.add_row()

            for column_name, column_value in record.items():
                import_table.set(row_number, column_name, column_value)

        import_table.save()

    def _format_data(self, data: Any, metadata: dict):
        """
        Allows to format JSON data before
        persisting it in database.

        Data should have a flat structure at the moment
        when it's being inserted into database. (list[dict])
        """
        return data
