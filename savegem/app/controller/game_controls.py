from kui.component.progress_button import KamaProgressPushButton
from kui.core.app import KamaApplication
from kui.core.controller import WidgetController
from kui.core.shortcut import tr

from savegem.constants import UIRefreshEvent
from savegem.app.worker.download_worker import DownloadWorker
from savegem.app.worker.upload_worker import UploadWorker
from savegem.common.core.context import context
from savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind


def _done_subscriber(message_key: str):
    """
    Used to get callback that will get
    executed once worker1 has finished work.
    """

    application = KamaApplication()

    def callback(event: DoneEvent):
        # Only show notification if there was no error.
        if event.success:
            application.window.notification(tr(message_key))

    return callback


def _progress_subscriber(widget: KamaProgressPushButton):
    """
    Used to get callback that will get executed
    when worker1 sends update event.
    """
    return lambda event: widget.set_progress(event.progress)


def _error_subscriber(event: ErrorEvent):
    """
    Callback that will get executed
    when worker1 sends error event.
    """

    application = KamaApplication()

    if event.kind == EventKind.SavesDirectoryMissing:
        game_path = context().games.current.local_path
        message = tr("notification_ErrorSaveDirectoryMissing", game_path)
        application.window.notification(message)

    elif event.kind == EventKind.DriveMetadataMissing:
        application.window.notification(tr("label_StorageIsEmptyDesc"))

    elif event.kind == EventKind.ErrorUploadingToDrive:
        application.window.notification(tr("notification_ErrorUploadingToDrive"))


class DownloadButtonController(WidgetController):
    """
    Controller which is used to configure download button.
    """

    def setup(self, download_button: KamaProgressPushButton):

        def start_download():
            """
            Used to start download of save from cloud.
            """

            worker = DownloadWorker()

            worker.error.connect(_error_subscriber)
            worker.progress.connect(_progress_subscriber(download_button))
            worker.completed.connect(download_button.refresh)
            worker.completed.connect(lambda: self.manager.event_refresh(UIRefreshEvent.SaveDownloaded))
            worker.completed.connect(_done_subscriber("notification_NewSaveHasBeenDownloaded"))
            worker.completed.connect(lambda: context().games.current.meta.local.calculate_checksum())

            self._do_work(worker)

        application = KamaApplication()

        download_button.clicked.connect(  # noqa
            lambda: application.window.confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                start_download
            )
        )


class UploadButtonController(WidgetController):
    """
    Controller which is used to configure upload button.
    """

    def setup(self, upload_button: KamaProgressPushButton):

        def start_upload():
            """
            Used to start upload of save to cloud.
            """

            worker = UploadWorker()

            worker.error.connect(_error_subscriber)
            worker.progress.connect(_progress_subscriber(upload_button))
            worker.completed.connect(upload_button.refresh)
            worker.completed.connect(lambda: context().games.current.meta.drive.refresh())
            worker.completed.connect(_done_subscriber("notification_SaveHasBeenUploaded"))

            self._do_work(worker)

        upload_button.clicked.connect(start_upload)  # noqa
