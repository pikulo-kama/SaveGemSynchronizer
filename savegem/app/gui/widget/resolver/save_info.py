from datetime import datetime, date

import pytz
from babel.dates import format_datetime
from babel.localtime import get_localzone

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.core.text_resource import tr


_status_desc_map = {
    SyncStatus.LocalOnly: "label_StorageIsEmptyDesc",
    SyncStatus.NoInformation: "label_NoInformationAboutCurrentSaveVersionDesc",
    SyncStatus.UpToDate: "info_SaveIsUpToDateDesc",
    SyncStatus.NeedsDownload: "info_SaveNeedsToBeDownloadedDesc",
    SyncStatus.NeedsUpload: "info_SaveNeedsToBeUploadedDesc"
}

_status_label_map = {
    SyncStatus.LocalOnly: "label_StorageIsEmpty",
    SyncStatus.NoInformation: "label_NoInformationAboutCurrentSaveVersion",
    SyncStatus.UpToDate: "info_SaveIsUpToDate",
    SyncStatus.NeedsDownload: "info_SaveNeedsToBeDownloaded",
    SyncStatus.NeedsUpload: "info_SaveNeedsToBeUploaded"
}

_status_icon_map = {
    SyncStatus.LocalOnly: "warning.svg",
    SyncStatus.NoInformation: "warning.svg",
    SyncStatus.UpToDate: "checkmark.svg",
    SyncStatus.NeedsDownload: "warning.svg",
    SyncStatus.NeedsUpload: "warning.svg"
}


class SaveInfoResolver(ContentResolver):
    """
    Used to resolve current cloud save information
    tokens.
    """

    def resolve(self, key: str, **kw):

        if key == "uploadDate":
            return self.__get_creation_date_info()[0]

        elif key == "uploadTime":
            return self.__get_creation_date_info()[1]

        elif key == "owner":
            return self.__get_owner()

        sync_status = app().games.current.meta.sync_status

        if key == "status":
            return tr(_status_label_map.get(sync_status))

        elif key == "statusDescription":
            return tr(_status_desc_map.get(sync_status))

        elif key == "statusIcon":
            return _status_icon_map.get(sync_status)

    @staticmethod
    def __get_owner():
        """
        Used to get name of person who uploaded current
        save to drive.
        """

        metadata = app().games.current.meta.drive

        if not metadata.is_present:
            return ""

        return metadata.owner

    @staticmethod
    def __get_creation_date_info():
        """
        Used to get text version of date and time
        when current save was uploaded to drive.
        """

        metadata = app().games.current.meta.drive

        if not metadata.is_present:
            return "", ""

        creation_datetime_naive = datetime.strptime(metadata.created_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_datetime = pytz.utc.localize(creation_datetime_naive)
        time_zone = pytz.timezone(str(get_localzone()))
        creation_datetime = utc_datetime.astimezone(time_zone)

        date_format = "d MMMM"

        # Only show year if it's not current one, just to avoid extra information.
        if creation_datetime.year != date.today().year:
            date_format += " YYYY"

        creation_date = format_datetime(creation_datetime, date_format, locale=app().state.locale)
        creation_time = creation_datetime.strftime("%H:%M")

        return creation_date, creation_time
