from datetime import date

from kui.core.app import KamaApplication
from kui.core.resolver import ContentResolver
from kui.core.shortcut import tr
from kutil.date import string_to_date, get_verbose_date, get_verbose_time
from kutil.logger import get_logger
from savegem.common.core.context import context
from savegem.common.core.save_meta import SyncStatus
from savegem.constants import TimeFormat

_logger = get_logger(__name__)

_status_label_map = {
    SyncStatus.LocalOnly: "label_StorageIsEmpty",
    SyncStatus.NoInformation: "label_NoInformationStatus",
    SyncStatus.NeedsDownload: "info_SaveNeedsToBeDownloaded",
    SyncStatus.NeedsUpload: "info_SaveNeedsToBeUploaded"
}

_status_desc_map = {
    SyncStatus.LocalOnly: "label_StorageIsEmptyDesc",
    SyncStatus.NoInformation: "label_NoInformationStatusDesc",
    SyncStatus.NeedsDownload: "info_SaveNeedsToBeDownloadedDesc",
    SyncStatus.NeedsUpload: "info_SaveNeedsToBeUploadedDesc"
}

_status_icon_map = {
    SyncStatus.LocalOnly: "upload_warning.svg",
    SyncStatus.NoInformation: "exclamation_mark.svg",
    SyncStatus.NeedsDownload: "download_warning.svg",
    SyncStatus.NeedsUpload: "upload_warning.svg"
}


class SaveInfoResolver(ContentResolver):
    """
    Used to resolve current cloud save information
    tokens.
    """

    def resolve(self, key: str, *args, **kw):
        na_label = tr("label_NA")

        if context().games.current is None:
            return na_label

        if key == "size":
            return self.__get_save_size() or na_label

        elif key == "uploadDate":
            return self.__get_creation_date_info()[0] or na_label

        elif key == "uploadTime":
            return self.__get_creation_date_info()[1]

        elif key == "ownerName":
            return self.__get_owner_property(lambda user: user.short_name) or na_label

        elif key == "ownerPhoto":
            return self.__get_owner_property(lambda user: user.photo) or "person.svg"

        sync_status = context().games.current.meta.sync_status

        if key == "status":
            return tr(_status_label_map.get(sync_status))

        elif key == "statusDescription":
            return tr(_status_desc_map.get(sync_status))

        elif key == "statusIcon":
            return _status_icon_map.get(sync_status)

        _logger.debug("Unknown key was provided = %s", key)
        return na_label

    @staticmethod
    def __get_owner_property(function):
        """
        Used to get name of person who uploaded current
        save to drive.
        """

        metadata = context().games.current.meta.drive

        if not metadata.is_present:
            return None

        user = context().users.by_email(metadata.owner)

        if user is None:
            return None

        return function(user)

    @staticmethod
    def __get_creation_date_info():
        """
        Used to get text version of date and time
        when current save was uploaded to drive.
        """

        metadata = context().games.current.meta.drive

        if not metadata.is_present:
            return None, None

        application = KamaApplication()
        creation_datetime = string_to_date(metadata.created_time)

        # Don't show year if it's current year.
        creation_date = get_verbose_date(
            creation_datetime,
            locale=application.translations.locale,
            show_year=creation_datetime.year != date.today().year
        )

        creation_time = get_verbose_time(
            creation_datetime,
            use_military=context().state.time_format == TimeFormat.Military
        )

        return creation_date, creation_time

    @staticmethod
    def __get_save_size():

        metadata = context().games.current.meta.drive

        if not metadata.is_present or metadata.size < 0:
            return None

        size = metadata.size

        if size < 1000:
            return tr("label_SizeKilobytes", size)
        else:
            return tr("label_SizeMegabytes", size // 1024)
