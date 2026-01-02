from typing import Any, Final

from kui.component.progress_button import KamaProgressPushButton
from kui.component.widget import KamaWidget
from kui.core.app import KamaApplication
from kui.core.constants import QBool
from kui.core.controller import TemplateWidgetController
from kui.core.shortcut import tr
from kutil.date import string_to_date, get_verbose_date, get_verbose_time
from kutil.logger import get_logger

from savegem.constants import UIRefreshEvent, TimeFormat
from savegem.app.worker.download_worker import DownloadWorker
from savegem.common.core.context import context
from savegem.common.core.save_meta import DriveFileMetadata
from savegem.common.service.subscriptable import DoneEvent

_logger = get_logger(__name__)


class SaveHistoryListController(TemplateWidgetController):
    """
    Used to manager save history list.
    """

    HistoryRecordActive: Final = "active"

    def _get_data(self) -> list[Any]:
        return context().games.current.meta.drive

    def resolve(self, metadata: DriveFileMetadata, value: str, *args, **kw):
        if value == "version":
            return self.__get_upload_date_string(metadata)

        elif value == "owner":
            return self.__get_owner_string(metadata)

        return None

    @classmethod
    def handle__history_record(cls, history_record: KamaWidget, metadata: DriveFileMetadata):
        """
        Used to apply style property to history record if
        save file checksum matches local save checksum.
        """

        is_current_save = metadata.checksum == context().games.current.meta.local.checksum
        history_record.setProperty(cls.HistoryRecordActive, QBool(is_current_save))

    def handle__restore_button(self, restore_button: KamaProgressPushButton, metadata: DriveFileMetadata):
        """
        Used to manager restore button of history record.
        Will hide button if checksum matches local checksum
        and will also bind callback to the button.
        """

        def restore_version(file_id: str, button: KamaProgressPushButton):
            application = KamaApplication()

            return lambda: application.window.confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: self.__restore_version(file_id, button)
            )

        restore_button.clicked.connect(restore_version(metadata.id, restore_button))
        is_current_save = metadata.checksum == context().games.current.meta.local.checksum

        if is_current_save:
            self.manager.delete(lambda meta: meta.name == restore_button.metadata.name)

    def __restore_version(self, file_id: str, button: KamaProgressPushButton):
        """
        Used to start download of save from cloud.
        """

        def on_completed(event: DoneEvent):

            if event.success:
                application = KamaApplication()
                context().games.current.meta.drive.refresh()
                self.manager.event_refresh(UIRefreshEvent.SaveDownloaded)

                application.window.notification(tr("notification_NewSaveHasBeenDownloaded"))

        worker = DownloadWorker(file_id)

        worker.progress.connect(lambda event: button.set_progress(event.progress))
        worker.completed.connect(on_completed)

        _logger.debug("Restoring save with ID = %s for game %s", file_id, context().games.current.name)
        self._do_work(worker)

    @staticmethod
    def __get_upload_date_string(metadata: DriveFileMetadata):
        """
        Used to get date when provided save was uploaded.
        """

        application = KamaApplication()
        creation_datetime = string_to_date(metadata.created_time)
        creation_date = get_verbose_date(creation_datetime, locale=application.locale)
        creation_time = get_verbose_time(
            creation_datetime,
            use_military=context().state.time_format == TimeFormat.Military
        )

        return f"{creation_date} {creation_time}"

    @staticmethod
    def __get_owner_string(metadata: DriveFileMetadata):
        """
        Used to get owner of provided save.
        """

        owner = context().users.by_email(metadata.owner)

        if owner is None:
            return metadata.owner

        return owner.name
