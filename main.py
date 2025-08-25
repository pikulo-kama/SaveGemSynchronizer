# Needs to be first thing that is being imported when application starts.
import initializer

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.visitor.GameDropdownVisitor import GameDropdownVisitor
from src.gui.visitor.LanguageSwitchVisitor import LanguageSwitchVisitor
from src.gui.visitor.UIRefreshButtonVisitor import UIRefreshButtonVisitor

from src.service.Downloader import Downloader
from src.service.Uploader import Uploader
from src.gui.gui import GUI
from src.gui.popup.confirmation import Confirmation
from src.gui.visitor.CoreVisitor import CoreVisitor
from src.util.file import OUTPUT_DIR, cleanup_directory
from src.util.logger import get_logger

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
            Downloader.download()

        confirmation = Confirmation()
        confirmation.set_confirm_callback(internal_confirm)
        confirmation.show(tr("confirmation_ConfirmToDownloadSave"))

    logger.info("Initializing application.")

    window = GUI.instance()
    window.metadata_function = lambda: Downloader.get_last_save_metadata()

    window.add_button("label_UploadSaveToCloud", Uploader.upload, prop("primaryButton"))
    window.add_button("label_DownloadSaveFromCloud", confirm_before_download, prop("secondaryButton"))

    window.on_close(on_destroy)
    window.register_visitors([
        CoreVisitor(),
        UIRefreshButtonVisitor(),
        GameDropdownVisitor(),
        LanguageSwitchVisitor()
    ])

    window.build()
    logger.info("Application shut down.")


if __name__ == '__main__':
    main()
