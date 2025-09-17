import tkinter as tk

from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.window import _GUI
from savegem.app.gui.component.progress_button import ProgressButton
from savegem.app.gui.constants import TkState, TkCursor, UIRefreshEvent
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.popup.notification import notification
from savegem.app.gui.visitor import Visitor
from savegem.common.service.downloader import Downloader
from savegem.common.service.subscriptable import Event, EventType, EventKind, ProgressEvent
from savegem.common.service.uploader import Uploader
from savegem.common.util.logger import get_logger
from savegem.common.util.thread import execute_in_blocking_thread

_logger = get_logger(__name__)


class DownloadUploadButtonVisitor(Visitor):
    """
    Used to build upload and download buttons.
    Always enabled.
    """

    def __init__(self):
        super().__init__(
            UIRefreshEvent.LanguageChange,
            UIRefreshEvent.AfterUploadDownloadComplete
        )

        self.__download_button = None
        self.__upload_button = None

        self.__downloader = Downloader()
        self.__uploader = Uploader()

        self.__downloader.subscribe(self.__done_subscriber("notification_NewSaveHasBeenDownloaded"))
        self.__uploader.subscribe(self.__done_subscriber("notification_SaveHasBeenUploaded"))

        self.__downloader.subscribe(self.__error_subscriber)
        self.__uploader.subscribe(self.__error_subscriber)

    def visit(self, gui: _GUI):
        self.__add_buttons(gui)

    def refresh(self, gui: _GUI):

        upload_button_label = tr("label_UploadSaveToDrive")
        download_button_label = tr("label_DownloadSaveFromDrive")

        self.__upload_button.configure(
            text=upload_button_label,
            progress=0
        )
        _logger.debug("Upload button reloaded (%s)", upload_button_label)

        self.__download_button.configure(
            text=download_button_label,
            progress=0
        )
        _logger.debug("Download button reloaded (%s)", download_button_label)

    def enable(self, gui: "_GUI"):
        self.__upload_button.configure(state=TkState.Default, cursor=TkCursor.Hand)
        self.__download_button.configure(state=TkState.Default, cursor=TkCursor.Hand)

    def disable(self, gui: "_GUI"):
        self.__upload_button.configure(state=TkState.Disabled, cursor=TkCursor.Wait)
        self.__download_button.configure(state=TkState.Disabled, cursor=TkCursor.Wait)

    def __add_buttons(self, gui):
        """
        Used to render upload and download buttons.
        """

        button_frame = tk.Frame(gui.center)

        def upload_callback():
            self.__uploader.upload(app.games.current)
            gui.refresh(UIRefreshEvent.AfterUploadDownloadComplete)

        def download_callback():
            self.__downloader.download(app.games.current)
            gui.refresh(UIRefreshEvent.AfterUploadDownloadComplete)

        self.__upload_button = ProgressButton(
            button_frame,
            width=35,
            command=lambda: execute_in_blocking_thread(upload_callback),
            style="Primary.TButton"
        )

        self.__download_button = ProgressButton(
            button_frame,
            width=5,
            command=lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: execute_in_blocking_thread(download_callback)
            ),
            style="Secondary.TButton"
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
    def __progress_subscriber(widget: ProgressButton):

        def subscriber(event: ProgressEvent):
            if event.type == EventType.PROGRESS:
                widget.configure(
                    text=f"{int(event.progress * 100)}%",
                    progress=event.progress
                )

        return subscriber
