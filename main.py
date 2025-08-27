# Needs to be first thing that is being imported when application starts.
# noinspection PyUnresolvedReferences
import initializer
from src.gui.visitor.copyright import CopyrightVisitor

from src.gui.visitor.download_upload_button import DownloadUploadButtonVisitor
from src.gui.visitor.game_dropdown import GameDropdownVisitor
from src.gui.visitor.language_switch import LanguageSwitchVisitor
from src.gui.visitor.ui_refresh_button import UIRefreshButtonVisitor

from src.gui import GUI
from src.gui.visitor.save_status import SaveStatusVisitor
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
        SaveStatusVisitor(),
        DownloadUploadButtonVisitor(),
        UIRefreshButtonVisitor(),
        LanguageSwitchVisitor(),
        CopyrightVisitor()
    ])

    gui.before_destroy(teardown)
    gui.build()

    logger.info("Application shut down.")


def teardown():
    logger.info("Cleaning up 'output' directory.")
    cleanup_directory(OUTPUT_DIR)


if __name__ == "__main__":
    main()
