from constants import Directory
from savegem.common.util.file import cleanup_directory
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


def teardown():
    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(Directory.Output)
