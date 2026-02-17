from typing import Any, Final

from kui.component.progress_button import KamaProgressPushButton
from kui.component.widget import KamaWidget
from kui.core.app import KamaApplication
from kui.core.controller import TemplateWidgetController, TemplateWidgetContext
from kui.core.metadata import ControllerArgs
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

    def retrieve_data(self, args: ControllerArgs) -> list[Any]:
        return context().games.current.meta.drive

    def resolve(self, widget_context: TemplateWidgetContext, value: str, *args, **kw):
        if value == "version":
            return self.__get_upload_date_string(widget_context.element)

        elif value == "owner":
            return self.__get_owner_string(widget_context.element)

        return None

    @classmethod
    def handle__saveListRecord(cls, history_record: KamaWidget, widget_context: TemplateWidgetContext):  # noqa
        """
        Used to apply style property to history record if
        save file checksum matches local save checksum.
        """

        if widget_context.element.checksum == context().games.current.meta.local.checksum:
            history_record.add_class(cls.HistoryRecordActive)

    def handle__restoreButton(self, restore_button: KamaProgressPushButton, widget_context: TemplateWidgetContext):  # noqa
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

        restore_button.clicked.connect(restore_version(widget_context.element.id, restore_button))
        is_current_save = widget_context.element.checksum == context().games.current.meta.local.checksum

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
        self.work(worker)

    @staticmethod
    def __get_upload_date_string(metadata: DriveFileMetadata):
        """
        Used to get date when provided save was uploaded.
        """

        application = KamaApplication()
        creation_datetime = string_to_date(metadata.created_time)
        creation_date = get_verbose_date(creation_datetime, locale=application.translations.locale)
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
