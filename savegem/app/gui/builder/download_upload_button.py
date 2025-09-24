from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from savegem.app.gui.worker import QWorker
from savegem.app.gui.worker.download_worker import DownloadWorker
from savegem.app.gui.worker.upload_worker import UploadWorker
from savegem.common.core import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.window import _GUI
from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.constants import UIRefreshEvent, QAttr, QKind
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.popup.notification import notification
from savegem.app.gui.builder import UIBuilder
from savegem.common.service.subscriptable import EventKind, ErrorEvent
from savegem.common.util.logger import get_logger
from savegem.app.gui.thread import execute_in_blocking_thread

_logger = get_logger(__name__)


class DownloadUploadButtonBuilder(UIBuilder):
    """
    Used to build upload and download buttons.
    Always enabled.
    """

    def __init__(self):
        super().__init__(UIRefreshEvent.LanguageChange)

        self.__gui = None

        self.__download_button: QProgressPushButton
        self.__upload_button: QProgressPushButton

        self.__thread: QThread
        self.__worker: QWorker

    def build(self, gui: _GUI):
        self.__gui = gui
        self.__add_buttons(gui)

    def refresh(self, gui: _GUI):

        upload_button_label = tr("label_UploadSaveToDrive")
        download_button_label = tr("label_DownloadSaveFromDrive")

        self.__upload_button.setText(upload_button_label)
        self.__upload_button.set_progress(0)
        _logger.debug("Upload button reloaded (%s)", upload_button_label)

        self.__download_button.setText(download_button_label)
        self.__download_button.set_progress(0)
        _logger.debug("Download button reloaded (%s)", download_button_label)

    def __add_buttons(self, gui: _GUI):
        """
        Used to render upload and download buttons.
        """

        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(20)

        self.__upload_button = QProgressPushButton()
        self.__download_button = QProgressPushButton()

        self.__upload_button.clicked.connect(self.__start_upload)  # noqa
        self.__download_button.clicked.connect(  # noqa
            lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                self.__start_download
            )
        )

        self.__upload_button.setProperty(QAttr.Kind, QKind.Primary)
        self.__download_button.setProperty(QAttr.Kind, QKind.Secondary)

        self._add_interactable(self.__upload_button)
        self._add_interactable(self.__download_button)

        button_layout.addSpacing(30)
        button_layout.addWidget(self.__upload_button, stretch=8)
        button_layout.addWidget(self.__download_button, stretch=2)
        button_layout.addSpacing(30)

        gui.center.layout().addWidget(button_frame, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)

    def __start_download(self):
        """
        Used to start download of save from cloud.
        """

        self.__thread = QThread()
        self.__worker = DownloadWorker()

        self.__worker.error.connect(self.__error_subscriber)
        self.__worker.progress.connect(self.__progress_subscriber(self.__download_button))
        self.__worker.completed.connect(self.__done_subscriber("notification_NewSaveHasBeenDownloaded"))

        execute_in_blocking_thread(self.__thread, self.__worker)

    def __start_upload(self):
        """
        Used to start upload of save to cloud.
        """

        self.__thread = QThread()
        self.__worker = UploadWorker()

        self.__worker.error.connect(self.__error_subscriber)
        self.__worker.progress.connect(self.__progress_subscriber(self.__upload_button))
        self.__worker.completed.connect(self.__done_subscriber("notification_SaveHasBeenUploaded"))

        execute_in_blocking_thread(self.__thread, self.__worker)

    def __done_subscriber(self, message: str):
        """
        Used to get callback that will get
        executed once worker has finished work.
        """

        def callback():
            notification(tr(message))
            self.refresh(self.__gui)

        return callback

    @staticmethod
    def __progress_subscriber(widget: QProgressPushButton):
        """
        Used to get callback that will get executed
        when worker sends update event.
        """
        return lambda event: widget.set_progress(event.progress)

    @staticmethod
    def __error_subscriber(event: ErrorEvent):
        """
        Callback that will get executed
        when worker sends error event.
        """

        if event.kind == EventKind.SAVES_DIRECTORY_IS_MISSING:
            notification(tr("notification_ErrorSaveDirectoryMissing", app.games.current.local_path))

        elif event.kind == EventKind.LAST_SAVE_METADATA_IS_NONE:
            notification(tr("label_StorageIsEmpty"))

        elif event.kind == EventKind.ERROR_UPLOADING_TO_DRIVE:
            notification(tr("notification_ErrorUploadingToDrive"))
