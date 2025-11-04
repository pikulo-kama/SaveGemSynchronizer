from savegem.app.gui.component.label import QCustomLabel
from savegem.app.gui.component.layout import QCustomVBoxLayout, QCustomHBoxLayout, QCustomLayout
from savegem.app.gui.component.list import QScrollableWidget
from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.component.spacer import QSpacer
from savegem.app.gui.component.widget import QCustomWidget
from savegem.app.gui.constants import UIRefreshEvent, QBool
from savegem.app.gui.controller import WidgetController
from savegem.app.gui.popup.confirmation import confirmation
from savegem.app.gui.popup.notification import notification
from savegem.app.gui.worker.download_worker import DownloadWorker
from savegem.common.core.context import app
from savegem.common.core.save_meta import DriveFileMetadata
from savegem.common.core.text_resource import tr
from savegem.common.service.subscriptable import DoneEvent
from savegem.common.util.date import string_to_date, get_verbose_date, get_verbose_time


class SaveHistoryListController(WidgetController):
    """
    Used to build and manage list of available save files on cloud.
    """

    def refresh(self, save_list: QScrollableWidget):

        save_list_layout: QCustomLayout = save_list.layout()
        self.manager.remove_child_widgets(save_list)

        def restore_version(file_id: str, button: QProgressPushButton):
            return lambda: confirmation(
                tr("confirmation_ConfirmToDownloadSave"),
                lambda: self.__restore_version(file_id, button)
            )

        for metadata in app().games.current.meta.drive.list:

            is_current_save = metadata.checksum == app().games.current.meta.local.checksum

            # Contains save file entry.
            record_container = QCustomWidget()
            record_container.setObjectName("saveListRecord")
            record_container.setProperty("active", QBool(is_current_save))
            record_container.setFixedHeight(70)
            record_container_layout = QCustomHBoxLayout(record_container)

            # Wrapper for upload date and owner.
            details_container = QCustomWidget()
            details_container_layout = QCustomVBoxLayout(details_container)

            version_label = QCustomLabel()
            version_label.setObjectName("saveListRecordVersion")
            version_label.setText(self.__get_upload_date_string(metadata))

            owner_label = QCustomLabel()
            owner_label.setObjectName("saveListRecordOwner")
            owner_label.setText(self.__get_owner_string(metadata))

            # Button to restore specific version.
            restore_button = QProgressPushButton()
            restore_button.setText(tr("label_Restore"))
            restore_button.clicked.connect(restore_version(metadata.id, restore_button))  # noqa

            save_list.layout().add_dynamic_widget(record_container)

            record_container_layout.add_dynamic_widget(details_container)
            record_container_layout.add_dynamic_widget(QSpacer())

            # Don't show restore button if checksum
            # of drive save matches checksum of local save.
            if not is_current_save:
                record_container_layout.add_dynamic_widget(restore_button)

            details_container_layout.add_dynamic_widget(version_label)
            details_container_layout.add_dynamic_widget(owner_label)

        save_list_layout.add_dynamic_widget(QSpacer())

    def __restore_version(self, file_id: str, button: QProgressPushButton):
        """
        Used to start download of save from cloud.
        """

        def on_completed(event: DoneEvent):

            if event.success:
                app().games.current.meta.drive.refresh()
                self.manager.gui.refresh(UIRefreshEvent.SaveDownloaded)

                notification(tr("notification_NewSaveHasBeenDownloaded"))

        worker = DownloadWorker(file_id)

        worker.progress.connect(lambda event: button.set_progress(event.progress))
        worker.completed.connect(on_completed)

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

        owner = app().user.by_email(metadata.owner)

        if owner is None:
            return metadata.owner

        return owner.name
