from src.util.file import cleanup_directory, OUTPUT_DIR
from src.util.logger import get_logger

logger = get_logger(__name__)


def teardown():
    logger.info("Cleaning up 'output' directory.")
    cleanup_directory(OUTPUT_DIR)
