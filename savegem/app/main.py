# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
from savegem.common import initializer
from savegem.common.cleanup import teardown

from savegem.app.gui import gui
from savegem.common.util.logger import get_logger
from savegem.common.service.gdrive import GDrive
from savegem.common.core import app

_logger = get_logger("main")


def _main():
    """
    Application entry point.
    """

    _logger.info("Initializing application.")

    app.user.initialize(GDrive.get_current_user())
    app.games.download()

    gui.initialize()
    gui.before_destroy(teardown)
    gui.build()

    _logger.info("Application shut down.")


if __name__ == "__main__":
    _main()
