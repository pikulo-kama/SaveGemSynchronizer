# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer
from cleanup import teardown

from src.gui import gui
from src.util.logger import get_logger

_logger = get_logger(__name__)


def main():
    """
    Application entry point.
    """

    _logger.info("Initializing application.")

    gui.initialize()
    gui.before_destroy(teardown)
    gui.build()

    _logger.info("Application shut down.")


if __name__ == "__main__":
    main()
