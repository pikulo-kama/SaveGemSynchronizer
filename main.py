# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer
from cleanup import teardown

from src.gui import GUI
from src.util.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Application entry point.
    """

    logger.info("Initializing application.")

    gui = GUI.instance()
    gui.before_destroy(teardown)
    gui.build()

    logger.info("Application shut down.")


if __name__ == "__main__":
    main()
