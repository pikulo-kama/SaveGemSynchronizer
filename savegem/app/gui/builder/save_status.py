from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout
from babel.localtime import get_localzone

from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.core import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.core.text_resource import tr
from savegem.app.gui.builder import UIBuilder
from savegem.common.util.logger import get_logger
from datetime import date, datetime

from babel.dates import format_datetime
from pytz import timezone


_logger = get_logger(__name__)

_status_message_map = {
    SyncStatus.LocalOnly: "label_StorageIsEmpty",
    SyncStatus.NoInformation: "label_NoInformationAboutCurrentSaveVersion",
    SyncStatus.UpToDate: "info_SaveIsUpToDate",
    SyncStatus.NeedsDownload: "info_SaveNeedsToBeDownloaded",
    SyncStatus.NeedsUpload: "info_SaveNeedsToBeUploaded"
}


class SaveStatusBuilder(UIBuilder):
    """
    Used to build elements displaying:
    - Last drive save information
    - Local save status information

    Always enabled.
    """

    def __init__(self):
        super().__init__(
            UIRefreshEvent.LanguageChange,
            UIRefreshEvent.GameConfigChange,
            UIRefreshEvent.CloudSaveFilesChange,
            UIRefreshEvent.GameSelectionChange,
            UIRefreshEvent.SaveDownloaded
        )

        self.__save_status: Optional[QLabel] = None
        self.__last_save_timestamp: Optional[QLabel] = None

    def build(self):
        """
        Used to render both local and Google Drive save status labels.
        """

        info_frame = QWidget(self._gui.center)
        layout = QGridLayout(info_frame)
        layout.setSpacing(5)

        self.__save_status = QLabel()
        self.__last_save_timestamp = QLabel()

        self.__save_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__save_status.setObjectName("saveStatusLabel")
        self.__last_save_timestamp.setObjectName("saveStatusTimestamp")

        layout.addWidget(self.__save_status, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.__last_save_timestamp, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self._gui.center.layout().addWidget(info_frame, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def refresh(self):
        save_status_label = self.__get_last_download_version_text()
        last_save_timestamp_label = self.__get_last_save_info_text()

        self.__save_status.setText(save_status_label)
        _logger.debug("Save status label was reloaded. (%s)", save_status_label)

        self.__last_save_timestamp.setText(last_save_timestamp_label)
        _logger.debug("Last save information label was reloaded. (%s)", last_save_timestamp_label)

    @staticmethod
    def __get_last_save_info_text():
        """
        Used to get Google Drive save status label.
        """

        metadata = app.games.current.meta.drive

        if not metadata.is_present:
            return ""

        time_zone = str(get_localzone())
        date_format = "d MMMM"

        creation_datetime = datetime.strptime(metadata.created_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        creation_datetime += timezone(time_zone).utcoffset(creation_datetime)

        # Only show year if it's not current one, just to avoid extra information.
        if creation_datetime.year != date.today().year:
            date_format += " YYYY"

        creation_date = format_datetime(creation_datetime, date_format, locale=app.state.locale)
        creation_time = creation_datetime.strftime("%H:%M")

        return tr(
            "info_NewestSaveOnDriveInformation",
            creation_date,
            creation_time,
            metadata.owner
        )

    @staticmethod
    def __get_last_download_version_text():
        """
        Used to get local save status label.
        """

        message_key = _status_message_map.get(app.games.current.meta.sync_status)
        return tr(message_key)
