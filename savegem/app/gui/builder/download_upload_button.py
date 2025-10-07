from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from savegem.app.gui.worker.download_worker import DownloadWorker
from savegem.app.gui.worker.upload_worker import UploadWorker
from savegem.common.core.context import app
from savegem.common.core.text_resource import tr
from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.constants import UIRefreshEvent, QAttr, QKind
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.popup.notification import notification
from savegem.app.gui.builder import UIBuilder
from savegem.common.service.subscriptable import EventKind, ErrorEvent, DoneEvent
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class DownloadUploadButtonBuilder(UIBuilder):
    """
    Used to build upload and download buttons.
    Always enabled.
    """

    def __init__(self):
        super().__init__(UIRefreshEvent.LanguageChange)

        self.__download_button: Optional[QProgressPushButton] = None
        self.__upload_button: Optional[QProgressPushButton] = None

    def build(self):
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
        self.__upload_button.setProperty(QAttr.Id, "uploadButton")
        self.__download_button.setProperty(QAttr.Kind, QKind.Secondary)
        self.__download_button.setProperty(QAttr.Id, "downloadButton")

        self._add_interactable(self.__upload_button)
        self._add_interactable(self.__download_button)

        button_layout.addSpacing(30)
        button_layout.addWidget(self.__upload_button, stretch=8)
        button_layout.addWidget(self.__download_button, stretch=2)
        button_layout.addSpacing(30)

        self._gui.center.layout().addWidget(button_frame, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)

    def refresh(self):

        upload_button_label = tr("label_UploadSaveToDrive")

        self.__upload_button.set_progress(0)
        self.__download_button.set_progress(0)

        self.__upload_button.setText(upload_button_label)
        _logger.debug("Upload button reloaded (%s)", upload_button_label)

    def __start_download(self):
        """
        Used to start download of save from cloud.
        """

        worker = DownloadWorker()

        worker.error.connect(self.__error_subscriber)
        worker.progress.connect(self.__progress_subscriber(self.__download_button))
        worker.completed.connect(self.__done_subscriber("notification_NewSaveHasBeenDownloaded"))
        worker.completed.connect(lambda: self._gui.refresh(UIRefreshEvent.SaveDownloaded))
        worker.completed.connect(self.refresh)

        self._do_work(worker)

    def __start_upload(self):
        """
        Used to start upload of save to cloud.
        """

        worker = UploadWorker()

        worker.error.connect(self.__error_subscriber)
        worker.progress.connect(self.__progress_subscriber(self.__upload_button))
        worker.completed.connect(self.__done_subscriber("notification_SaveHasBeenUploaded"))
        worker.completed.connect(self.refresh)

        self._do_work(worker)

    @staticmethod
    def __done_subscriber(message: str):
        """
        Used to get callback that will get
        executed once worker has finished work.
        """

        def callback(event: DoneEvent):
            # Only show notification if there was no error.
            if event.success:
                notification(tr(message))

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

        if event.kind == EventKind.SavesDirectoryMissing:
            notification(tr("notification_ErrorSaveDirectoryMissing", app().games.current.local_path))

        elif event.kind == EventKind.DriveMetadataMissing:
            notification(tr("label_StorageIsEmpty"))

        elif event.kind == EventKind.ErrorUploadingToDrive:
            notification(tr("notification_ErrorUploadingToDrive"))
