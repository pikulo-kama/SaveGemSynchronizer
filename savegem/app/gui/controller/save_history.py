from typing import Any, Final

from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import UIRefreshEvent, QBool
from savegem.app.gui.controller import TemplateWidgetController
from savegem.app.gui.window import gui
from savegem.app.worker.download_worker import DownloadWorker
from savegem.common.core.context import app
from savegem.common.core.save_meta import DriveFileMetadata
from savegem.common.core.text_resource import tr
from savegem.common.service.subscriptable import DoneEvent
from savegem.common.util.date import string_to_date, get_verbose_date, get_verbose_time
from savegem.common.util.logger import get_logger

_logger = get_logger(__name__)


class SaveHistoryListController(TemplateWidgetController):
    """
    Used to manager save history list.
    """

    HistoryRecordActive: Final = "active"

    def _get_data(self) -> list[Any]:
        return app().games.current.meta.drive

    def resolve(self, metadata: DriveFileMetadata, value: str, *args, **kw):
        if value == "version":
            return self.__get_upload_date_string(metadata)

        elif value == "owner":
            return self.__get_owner_string(metadata)

        return None

    @classmethod
    def handle__history_record(cls, history_record: QCustomWidget, metadata: DriveFileMetadata):
        """
        Used to apply style property to history record if
        save file checksum matches local save checksum.
        """

        is_current_save = metadata.checksum == app().games.current.meta.local.checksum
        history_record.setProperty(cls.HistoryRecordActive, QBool(is_current_save))

    def handle__restore_button(self, restore_button: QProgressPushButton, metadata: DriveFileMetadata):
        """
        Used to manager restore button of history record.
        Will hide button if checksum matches local checksum
        and will also bind callback to the button.
        """

        def restore_version(file_id: str, button: QProgressPushButton):
            return lambda: gui().confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: self.__restore_version(file_id, button)
            )

        restore_button.clicked.connect(restore_version(metadata.id, restore_button))
        is_current_save = metadata.checksum == app().games.current.meta.local.checksum

        if is_current_save:
            self.manager.delete(lambda meta: meta.name == restore_button.metadata.name)

    def __restore_version(self, file_id: str, button: QProgressPushButton):
        """
        Used to start download of save from cloud.
        """

        def on_completed(event: DoneEvent):

            if event.success:
                app().games.current.meta.drive.refresh()
                self.manager.event_refresh(UIRefreshEvent.SaveDownloaded)

                gui().notification(tr("notification_NewSaveHasBeenDownloaded"))

        worker = DownloadWorker(file_id)

        worker.progress.connect(lambda event: button.set_progress(event.progress))
        worker.completed.connect(on_completed)

        _logger.debug("Restoring save with ID = %s for game %s", file_id, app().games.current.name)
        self._do_work(worker)

    @staticmethod
    def __get_upload_date_string(metadata: DriveFileMetadata):
        """
        Used to get date when provided save was uploaded.
        """

        creation_datetime = string_to_date(metadata.created_time)
        creation_date = get_verbose_date(creation_datetime)
        creation_time = get_verbose_time(creation_datetime)

        return f"{creation_date} {creation_time}"

    @staticmethod
    def __get_owner_string(metadata: DriveFileMetadata):
        """
        Used to get owner of provided save.
        """

        owner = app().users.by_email(metadata.owner)

        if owner is None:
            return metadata.owner

        return owner.name
