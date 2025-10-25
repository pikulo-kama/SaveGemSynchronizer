import argparse
import os
import sys

from savegem.initializer.extractor import invoke_extractor, get_extractors, RegularExtractorName

from savegem.initializer.importer import invoke_importer
from savegem.initializer.db_initializer import DatabaseInitializer


def main():
    """
    Command line tool
    that is used to perform database related operations.
    """

    parser = argparse.ArgumentParser(
        description="Database Management Service for SaveGem.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(
        title="Available Commands",
        dest="command",
        required=True,
        help="Select an operation to perform."
    )

    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Run Python-based database schema migrations."
    )

    import_parser = subparsers.add_parser(
        "import",
        help="Import table data from JSON definitions in source files."
    )

    import_parser.add_argument(
        "--definition_file",
        type=str,
        help="Name of the file containing names of table definitions that needs to be imported."
    )

    import_parser.add_argument(
        "--file_name",
        type=str,
        help="Name of the import that needs to be imported"
    )

    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract table data from database tables into JSON definitions"
    )

    extract_types = [name.replace("Extractor", "") for name, _ in get_extractors()]
    extract_types.insert(0, RegularExtractorName)

    extract_parser.add_argument(
        "--type",
        default=RegularExtractorName,
        choices=extract_types,
        type=str,
        help="Set type of data that is being extracted."
    )

    extract_parser.add_argument(
        '--output',
        default=os.path.join("output", "extract"),
        type=str,
        help='Output directory where extracted data would be placed.'
    )

    extract_parser.add_argument(
        "--table_name",
        required=True,
        type=str,
        help="Name of the table that should be extracted."
    )

    migrate_parser.set_defaults(func=DatabaseInitializer.run)
    import_parser.set_defaults(func=invoke_importer)
    extract_parser.set_defaults(func=invoke_extractor)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    try:
        exit_code = args.func(args)
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nCritical Error during execution: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
