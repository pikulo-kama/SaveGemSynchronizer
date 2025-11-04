from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.popup.notification import notification
from savegem.app.gui.worker.download_worker import DownloadWorker
from savegem.app.gui.worker.upload_worker import UploadWorker
from savegem.common.core.context import app
from savegem.common.core.text_resource import tr
from savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind


def _done_subscriber(message: str):
    """
    Used to get callback that will get
    executed once worker has finished work.
    """

    def callback(event: DoneEvent):
        # Only show notification if there was no error.
        if event.success:
            notification(tr(message))

    return callback


def _progress_subscriber(widget: QProgressPushButton):
    """
    Used to get callback that will get executed
    when worker sends update event.
    """
    return lambda event: widget.set_progress(event.progress)


def _error_subscriber(event: ErrorEvent):
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


class DownloadButtonController(WidgetController):
    """
    Controller which is used to configure download button.
    """

    def setup(self, download_button: QProgressPushButton):

        def start_download():
            """
            Used to start download of save from cloud.
            """

            worker = DownloadWorker()

            worker.error.connect(_error_subscriber)
            worker.progress.connect(_progress_subscriber(download_button))
            worker.completed.connect(_done_subscriber("notification_NewSaveHasBeenDownloaded"))
            worker.completed.connect(lambda: self.manager.gui.refresh(UIRefreshEvent.SaveDownloaded))
            worker.completed.connect(download_button.refresh)

            self._do_work(worker)

        download_button.clicked.connect(  # noqa
            lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                start_download
            )
        )


class UploadButtonController(WidgetController):
    """
    Controller which is used to configure upload button.
    """

    def setup(self, upload_button: QProgressPushButton):

        def start_upload():
            """
            Used to start upload of save to cloud.
            """

            worker = UploadWorker()

            worker.error.connect(_error_subscriber)
            worker.progress.connect(_progress_subscriber(upload_button))
            worker.completed.connect(_done_subscriber("notification_SaveHasBeenUploaded"))
            worker.completed.connect(upload_button.refresh)
            worker.completed.connect(lambda: app().games.current.meta.drive.refresh())

            self._do_work(worker)

        upload_button.clicked.connect(start_upload)  # noqa
