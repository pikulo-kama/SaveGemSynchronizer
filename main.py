# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer

from src.gui.visitor.DownloadUploadButtonVisitor import DownloadUploadButtonVisitor
from src.gui.visitor.GameDropdownVisitor import GameDropdownVisitor
from src.gui.visitor.LanguageSwitchVisitor import LanguageSwitchVisitor
from src.gui.visitor.UIRefreshButtonVisitor import UIRefreshButtonVisitor

from src.gui.gui import GUI
from src.gui.visitor.CoreVisitor import CoreVisitor
from src.util.file import OUTPUT_DIR, cleanup_directory
from src.util.logger import get_logger

logger = get_logger(__name__)


def main():
    """
    Application entry point.
    """

    logger.info("Initializing application.")
    gui = GUI.instance()

    gui.register_visitors([
        # Needs to be initialized first.
        GameDropdownVisitor(),
        CoreVisitor(),
        DownloadUploadButtonVisitor(),
        UIRefreshButtonVisitor(),
        LanguageSwitchVisitor()
    ])

    gui.before_destroy(teardown)
    gui.build()

    logger.info("Application shut down.")


def teardown():
    logger.info("Cleaning up 'output' directory.")
    cleanup_directory(OUTPUT_DIR)


if __name__ == "__main__":
    main()
