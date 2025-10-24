import copy
import os
from datetime import datetime
from pathlib import Path

from constants import Directory, JSON_EXTENSION
from savegem.common.db.manager import db
from savegem.common.util.file import save_file
from savegem.common.util.reflection import get_members
from savegem.initializer.util import ExtractType


def invoke_extractor(args):
    """
    Used to call database extractor.
    Will use type provided to initializer
    to decide which implementation of extractor should
    be invoked.
    """

    extractor = DatabaseExtractor()

    for member_name, member in get_members(__package__, DatabaseExtractor):
        if member_name.lower().startswith(args.type.lower()):
            extractor = member()

    extractor.do_extract(args)


class DatabaseExtractor:
    """
    Database extractor.
    Used to extract table data and store it
    in JSON format.
    """

    def do_extract(self, args):
        """
        Used to extract data from table.
        """

        if args.type == ExtractType.Regular and args.table_name is None:
            print("Argument '--table_name' is required for Regular extract.")
            exit(1)

        table_name = self._get_table_name(args)
        table = db().table(table_name).retrieve()
        table_json = [row.to_json() for row in table]

        extract_file_path = Path(str(os.path.join(Directory().ProjectRoot, args.output, table_name + JSON_EXTENSION)))
        extract_file_path.parent.mkdir(parents=True, exist_ok=True)

        formatted_data = copy.deepcopy(table_json)

        for idx, record in enumerate(table_json):
            for column_name, column_value in record.items():
                if column_value is None:
                    del formatted_data[idx][column_name]

        table_definition = {
            "metadata": {
                "table_name": table_name,
                "extractor": self.__class__.__name__,
                "extract_date": datetime.now().isoformat()
            },
            "data": self._post_extract(formatted_data)
        }

        save_file(str(extract_file_path), table_definition, as_json=True)

    def _get_table_name(self, args):
        """
        Table name from which data is being
        extracted.
        """
        return args.table_name

    def _post_extract(self, data: any):
        """
        Allows to process retrieved table
        data and change data structure if
        needed.
        """
        return data
