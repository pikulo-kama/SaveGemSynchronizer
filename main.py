import os.path

from constants import APP_DATA_ROOT
from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.visitor.GameDropdownVisitor import GameDropdownVisitor
from src.gui.visitor.LanguageSwitchVisitor import LanguageSwitchVisitor

from src.service.downloader import Downloader
from src.service.uploader import Uploader
from src.gui.gui import GUI
from src.gui.popup.confirmation import Confirmation
from src.gui.visitor.CoreVisitor import CoreVisitor
from src.gui.visitor.XboxUserListVisitor import XboxUserListVisitor
from src.util.file import OUTPUT_DIR, cleanup_directory, LOGS_DIR
from src.util.logger import get_logger, initialize_logging

logger = get_logger(__name__)


def main():

    def on_destroy():
        logger.info("Cleaning up 'output' directory.")
        cleanup_directory(OUTPUT_DIR)
        logger.info("Destroying window.")
        window.destroy()

    def confirm_before_download():

        def internal_confirm():
            confirmation.destroy()
            downloader.download()

        confirmation = Confirmation()
        confirmation.set_confirm_callback(internal_confirm)
        confirmation.show(tr("confirmation_ConfirmToDownloadSave"))

    setup()
    logger.info("Initializing application.")

    downloader = Downloader()
    uploader = Uploader()

    window = GUI.instance()
    window.metadata_function = lambda: downloader.get_last_save_metadata()

    window.add_button("label_UploadSaveToCloud", uploader.upload, prop("primaryButton"))
    window.add_button("label_DownloadSaveFromCloud", confirm_before_download, prop("secondaryButton"))

    window.on_close(on_destroy)
    window.register_visitors([
        CoreVisitor(),
        GameDropdownVisitor(),
        LanguageSwitchVisitor(),
        XboxUserListVisitor()
    ])

    window.build()
    logger.info("Application shut down.")


def setup():

    for directory in [APP_DATA_ROOT, OUTPUT_DIR, LOGS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info("Creating '%s' directory.", directory)

    initialize_logging()


if __name__ == '__main__':
    main()
