import tkinter as tk
from tkinter import ttk

from src.core.text_resource import tr
from src.gui import GUI
from src.gui.component.wait_button import WaitButton
from src.gui.popup.confirmation import confirmation
from src.gui.visitor import Visitor
from src.service.downloader import Downloader
from src.service.uploader import Uploader
from src.util.logger import get_logger
from src.util.thread import execute_in_thread

logger = get_logger(__name__)


class DownloadUploadButtonVisitor(Visitor):
    """
    Used to build upload and download buttons.
    Always enabled.
    """

    def __init__(self):
        self.__download_button = None
        self.__upload_button = None

    def visit(self, gui: GUI):
        self.__add_buttons(gui)

    def refresh(self, gui: GUI):

        upload_button_label = tr("label_UploadSaveToDrive")
        download_button_label = tr("label_DownloadSaveFromDrive")

        self.__upload_button.configure(text=upload_button_label)
        logger.debug("Upload button reloaded (%s)", upload_button_label)

        self.__download_button.configure(text=download_button_label)
        logger.debug("Download button reloaded (%s)", download_button_label)

    def is_enabled(self):
        return True

    def __add_buttons(self, gui):
        """
        Used to render upload and download buttons.
        """

        button_frame = tk.Frame(gui.body())

        self.__upload_button = WaitButton(
            button_frame,
            cursor="hand2",
            width=35,
            command=lambda: execute_in_thread(Uploader.upload),
            waitMessage=tr("label_UploadingSaveToDrive"),
            style="Primary.TButton",
            takefocus=False
        )

        self.__download_button = ttk.Button(
            button_frame,
            cursor="hand2",
            width=5,
            command=lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: execute_in_thread(Downloader.download)
            ),
            style="Secondary.TButton",
            takefocus=False
        )

        self.__upload_button.grid(row=0, column=0, padx=5)
        self.__download_button.grid(row=0, column=1, padx=5)
        button_frame.grid(row=1, column=0)
