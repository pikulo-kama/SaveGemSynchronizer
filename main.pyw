from constants import UPLOAD_LABEL, DOWNLOAD_LABEL, CONFIRMATION_BEFORE_DOWNLOAD_MSG, UPLOAD_BTN_PROPERTIES, \
    DOWNLOAD_BTN_PROPERTIES

from gui import GUI
from core import Downloader, Uploader
from gui.confirmation import Confirmation


def main():

    def on_destroy():
        Uploader.cleanup()
        window.destroy()

    def confirm_before_download():

        def internal_confirm():
            confirmation.destroy()
            Downloader().download()

        confirmation = Confirmation()
        confirmation.show_notification(CONFIRMATION_BEFORE_DOWNLOAD_MSG, internal_confirm)

    window = GUI()

    window.add_button(UPLOAD_LABEL, Uploader().upload, UPLOAD_BTN_PROPERTIES)
    window.add_button(DOWNLOAD_LABEL, confirm_before_download, DOWNLOAD_BTN_PROPERTIES)

    window.on_close(on_destroy)
    window.build()


if __name__ == '__main__':
    main()
