import copy
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from constants import Directory, JSON_EXTENSION
from savegem.common.db.manager import db
from savegem.common.util.file import save_file
from savegem.common.util.logger import get_logger
from savegem.common.util.reflection import get_members


RegularExtractorName = "Regular"
_logger = get_logger(__name__)


def invoke_extractor(args):
    """
    Used to call database extractor.
    Will use type provided to initializer
    to decide which implementation of extractor should
    be invoked.
    """

    extractor = RegularExtractor()
    target_extractor_name = f"{args.type}Extractor"

    for member_name, member in get_extractors():
        if target_extractor_name == member_name:
            extractor = member()
            break

    extractor.do_extract(args)


def get_extractors():
    """
    Used to get list of custom widget extractors.
    """
    return get_members(__package__, RegularExtractor)


class RegularExtractor:
    """
    Database extractor.
    Used to extract table data and store it
    in JSON format.
    """

    def do_extract(self, args):
        """
        Used to extract data from table.
        """

        _logger.info("Starting data extraction.")
        _logger.info("Extractor: %s", args.type)
        _logger.info("Table: %s", args.table_name)
        _logger.info("Output Directory: %s", args.output)

        table_name = args.table_name
        table = db().table(table_name)

        if args.filter:
            _logger.info("Filter: %s", args.filter)
            table.where(args.filter)

        table_json = [row.to_json() for row in table.retrieve()]

        extract_file_path = Path(str(os.path.join(Directory().ProjectRoot, args.output, table_name + JSON_EXTENSION)))
        extract_file_path.parent.mkdir(parents=True, exist_ok=True)

        formatted_data = copy.deepcopy(table_json)

        # Remove NULL values.
        for idx, record in enumerate(table_json):
            for column_name, column_value in record.items():
                if column_value is None:
                    del formatted_data[idx][column_name]

        content = {
            "metadata": {
                "table_name": table_name,
                "type": args.type,
                "extract_date": datetime.now().isoformat()
            },
            "data": self._post_extract(formatted_data)
        }

        if args.filter:
            content["metadata"]["filter"] = args.filter

        save_file(str(extract_file_path), content, as_json=True)

    def _post_extract(self, data: Any):
        """
        Allows to process retrieved table
        data and change data structure if
        needed.
        """
        return data
