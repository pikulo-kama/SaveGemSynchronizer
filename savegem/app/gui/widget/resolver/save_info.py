from datetime import date

from savegem.app.gui.widget.resolver import ContentResolver
from savegem.common.core.context import app
from savegem.common.core.save_meta import SyncStatus
from savegem.common.core.text_resource import tr
from savegem.common.util.date import string_to_date, get_verbose_time, get_verbose_date

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

    def resolve(self, key: str, *args, **kw):

        if key == "size":
            return self.__get_save_size()

        elif key == "uploadDate":
            return self.__get_creation_date_info()[0]

        elif key == "uploadTime":
            return self.__get_creation_date_info()[1]

        elif key == "ownerName":
            return self.__get_owner_property(lambda user: user.short_name)

        elif key == "ownerPhoto":
            return self.__get_owner_property(lambda user: user.photo)

        sync_status = app().games.current.meta.sync_status

        if key == "status":
            return tr(_status_label_map.get(sync_status))

        elif key == "statusDescription":
            return tr(_status_desc_map.get(sync_status))

        elif key == "statusIcon":
            return _status_icon_map.get(sync_status)

    @staticmethod
    def __get_owner_property(function):
        """
        Used to get name of person who uploaded current
        save to drive.
        """

        metadata = app().games.current.meta.drive

        if not metadata.is_present:
            return ""

        user = app().user.by_email(metadata.owner)

        if user is None:
            return ""

        return function(user)

    @staticmethod
    def __get_creation_date_info():
        """
        Used to get text version of date and time
        when current save was uploaded to drive.
        """

        metadata = app().games.current.meta.drive

        if not metadata.is_present:
            return "", ""

        creation_datetime = string_to_date(metadata.created_time)

        # Don't show year if it's current year.
        creation_date = get_verbose_date(creation_datetime, creation_datetime.year != date.today().year)
        creation_time = get_verbose_time(creation_datetime)

        return creation_date, creation_time

    @staticmethod
    def __get_save_size():

        metadata = app().games.current.meta.drive

        if not metadata.is_present or metadata.size < 0:
            return tr("label_NA")

        size = metadata.size

        if size < 1000:
            return tr("label_SizeKilobytes", size)
        else:
            return tr("label_SizeMegabytes", size // 1024)
