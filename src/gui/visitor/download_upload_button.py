import tkinter as tk
from tkinter import ttk

from src.core import app
from src.core.text_resource import tr
from src.gui import GUI
from src.gui.popup.confirmation import confirmation
from src.gui.popup.notification import notification
from src.gui.visitor import Visitor
from src.service.downloader import Downloader
from src.service.subscriptable import Event, EventType, EventKind, ProgressEvent
from src.service.uploader import Uploader
from src.util.logger import get_logger
from src.util.thread import execute_in_thread

_logger = get_logger(__name__)


class DownloadUploadButtonVisitor(Visitor):
    """
    Used to build upload and download buttons.
    Always enabled.
    """

    def __init__(self):

        self.__download_button = None
        self.__upload_button = None

        self.__downloader = Downloader()
        self.__uploader = Uploader()

        self.__downloader.subscribe(self.__done_subscriber("notification_NewSaveHasBeenDownloaded"))
        self.__uploader.subscribe(self.__done_subscriber("notification_SaveHasBeenUploaded"))

        self.__downloader.subscribe(self.__error_subscriber)
        self.__uploader.subscribe(self.__error_subscriber)

    def visit(self, gui: GUI):
        self.__add_buttons(gui)

    def refresh(self, gui: GUI):

        upload_button_label = tr("label_UploadSaveToDrive")
        download_button_label = tr("label_DownloadSaveFromDrive")

        self.__upload_button.configure(text=upload_button_label)
        _logger.debug("Upload button reloaded (%s)", upload_button_label)

        self.__download_button.configure(text=download_button_label)
        _logger.debug("Download button reloaded (%s)", download_button_label)

    def is_enabled(self):
        return True

    def __add_buttons(self, gui):
        """
        Used to render upload and download buttons.
        """

        button_frame = tk.Frame(gui.body())

        self.__upload_button = ttk.Button(
            button_frame,
            cursor="hand2",
            width=35,
            command=lambda: execute_in_thread(self.__uploader.upload),
            style="Primary.TButton",
            takefocus=False
        )

        self.__download_button = ttk.Button(
            button_frame,
            cursor="hand2",
            width=5,
            command=lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: execute_in_thread(self.__downloader.download)
            ),
            style="Secondary.TButton",
            takefocus=False
        )

        self.__uploader.subscribe(self.__progress_subscriber(self.__upload_button))
        self.__downloader.subscribe(self.__progress_subscriber(self.__download_button))

        self.__upload_button.grid(row=0, column=0, padx=5)
        self.__download_button.grid(row=0, column=1, padx=5)

        button_frame.grid(row=1, column=0)

    @staticmethod
    def __done_subscriber(message: str):

        def subscriber(event: Event):
            if event.type == EventType.DONE:
                GUI.instance().refresh()
                notification(tr(message))

        return subscriber

    @staticmethod
    def __error_subscriber(event: Event):

        if event.type is not EventType.ERROR:
            return

        if event.kind == EventKind.SAVES_DIRECTORY_IS_MISSING:
            notification(tr("notification_ErrorSaveDirectoryMissing", app.games.current.local_path))

        elif event.kind == EventKind.LAST_SAVE_METADATA_IS_NONE:
            notification(tr("label_StorageIsEmpty"))

        elif event.kind == EventKind.ERROR_UPLOADING_TO_DRIVE:
            notification(tr("notification_ErrorUploadingToDrive"))

    @staticmethod
    def __progress_subscriber(widget):

        def subscriber(event: ProgressEvent):
            if event.type == EventType.PROGRESS:
                widget.configure(text=f"{int(event.progress * 100)}%")

        return subscriber
