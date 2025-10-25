from savegem.app.ipc_socket import ui_socket
from savegem.common.core.ipc_socket import IPCCommand
from savegem.common.db.manager import db
from savegem.common.util.file import read_file, resolve_import_data
from savegem.common.util.reflection import get_members


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

    # Handle definition_file argument.
    for line in definition_file.split("\n"):
        line = line.strip()

        # Allow comments and skip empty lines.
        if line.startswith("#") or len(line) == 0:
            continue

        files_to_import.append(line)

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
            print("Argument '--file_name' is required for import.")
            exit(1)

        import_file = read_file(resolve_import_data(args.file_name), as_json=True)
        table_name = import_file.get("metadata", {}).get("table_name")
        data: list[dict] = import_file.get("data", [])
        data = self._format_data(data)

        import_table = db().table(table_name).retrieve()

        # Remove all existing data.
        import_table.remove_all()
        import_table.save()

        for record in data:
            row_number = import_table.add_row()

            for column_name, column_value in record.items():
                import_table.set(row_number, column_name, column_value)

        import_table.save()

    def _format_data(self, data: any):
        """
        Allows to format JSON data before
        persisting it in database.

        Data should have a flat structure at the moment
        when it's being inserted into database. (list[dict])
        """
        return data
