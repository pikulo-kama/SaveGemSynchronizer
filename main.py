# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer
from cleanup import teardown

from src.gui import gui
from src.util.logger import get_logger

_logger = get_logger("main")


def _main():
    """
    Application entry point.
    """

    _logger.info("Initializing application.")

    from src.core import app
    from src.service.gdrive import GDrive

    app.user.initialize(GDrive.get_current_user())
    app.games.download()

    gui.initialize()
    gui.before_destroy(teardown)
    gui.build()

    _logger.info("Application shut down.")


if __name__ == "__main__":
    _main()
