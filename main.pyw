import os.path

from constants import UPLOAD_LABEL, DOWNLOAD_LABEL, CONFIRMATION_BEFORE_DOWNLOAD_MSG, UPLOAD_BTN_PROPERTIES, \
    DOWNLOAD_BTN_PROPERTIES

from gui import GUI
from core import Downloader, Uploader
from gui.popup.confirmation import Confirmation


def main():

    def on_destroy():
        Uploader.cleanup()
        window.destroy()

    def confirm_before_download():

        def internal_confirm():
            confirmation.destroy()
            downloader.download()

        confirmation = Confirmation()
        confirmation.show_confirmation(CONFIRMATION_BEFORE_DOWNLOAD_MSG, internal_confirm)

    setup()

    downloader = Downloader()
    uploader = Uploader()

    window = GUI.instance()
    window.set_last_save_func(lambda: downloader.download_last_save())

    window.add_button(UPLOAD_LABEL, uploader.upload, UPLOAD_BTN_PROPERTIES)
    window.add_button(DOWNLOAD_LABEL, confirm_before_download, DOWNLOAD_BTN_PROPERTIES)

    window.on_close(on_destroy)
    window.build()


def setup():

    # Create 'output' directory if not exists
    if not os.path.exists(Uploader.output_dir):
        os.makedirs(Uploader.output_dir)


if __name__ == '__main__':
    main()
