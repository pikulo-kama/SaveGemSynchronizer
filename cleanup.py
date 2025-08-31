from constants import Directory
from src.util.file import cleanup_directory
from src.util.logger import get_logger

_logger = get_logger(__name__)


def teardown():
    _logger.info("Cleaning up 'output' directory.")
    cleanup_directory(Directory.Output)
