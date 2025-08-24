import os.path
import shutil

from constants import APP_DATA_ROOT
from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.visitor.GameDropdownVisitor import GameDropdownVisitor

from src.service.downloader import Downloader
from src.service.uploader import Uploader
from src.gui.gui import GUI
from src.gui.popup.confirmation import Confirmation
from src.gui.visitor.CoreVisitor import CoreVisitor
from src.gui.visitor.XboxUserListVisitor import XboxUserListVisitor
from src.util.file import OUTPUT_DIR, resolve_temp_file, cleanup_directory


def main():

    def on_destroy():
        cleanup_directory(OUTPUT_DIR)
        window.destroy()

    def confirm_before_download():

        def internal_confirm():
            confirmation.destroy()
            downloader.download()

        confirmation = Confirmation()
        confirmation.show_confirmation(tr("confirmation_ConfirmToDownloadSave"), internal_confirm)

    setup()

    downloader = Downloader()
    uploader = Uploader()

    window = GUI.instance()
    window.last_save_func = lambda: downloader.get_last_save_metadata()

    window.add_button(tr("label_UploadSaveToCloud"), uploader.upload, prop("primaryButton"))
    window.add_button(tr("label_DownloadSaveFromCloud"), confirm_before_download, prop("secondaryButton"))

    window.on_close(on_destroy)
    window.build([
        CoreVisitor(),
        GameDropdownVisitor(),
        XboxUserListVisitor()
    ])


def setup():
    if not os.path.exists(APP_DATA_ROOT):
        os.makedirs(APP_DATA_ROOT)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


if __name__ == '__main__':
    main()
