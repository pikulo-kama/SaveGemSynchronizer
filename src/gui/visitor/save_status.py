import tkinter as tk

from babel.localtime import get_localzone

from src.core import app
from src.core.text_resource import tr
from src.core.holders import prop
from src.gui import GUI
from src.gui.visitor import Visitor
from datetime import date, datetime

from babel.dates import format_datetime
from pytz import timezone

from src.service.downloader import Downloader
from src.util.logger import get_logger

logger = get_logger(__name__)


class SaveStatusVisitor(Visitor):
    """
    Used to build elements displaying:
    - Last drive save information
    - Local save status information

    Always enabled.
    """

    def __init__(self):
        self.__save_status = None
        self.__last_save_timestamp = None

    def visit(self, gui: GUI):
        self.__add_save_information(gui)

    def refresh(self, gui: GUI):
        last_save_meta = Downloader.get_last_save_metadata()

        save_status_label = self.__get_last_download_version_text(last_save_meta)
        last_save_timestamp_label = self.__get_last_save_info_text(last_save_meta)

        self.__save_status.configure(text=save_status_label)
        logger.debug("Save status label was reloaded. (%s)", save_status_label)

        self.__last_save_timestamp.configure(text=last_save_timestamp_label)
        logger.debug("Last save information label was reloaded. (%s)", last_save_timestamp_label)

    def is_enabled(self):
        return True

    def __add_save_information(self, gui):
        """
        Used to render both local and Google Drive save status labels.
        """

        info_frame = tk.Frame(gui.body())

        # Text is empty for fields at this moment
        # They would be populated later by GUI component.
        self.__save_status = tk.Label(
            info_frame,
            fg=prop("primaryColor"),
            font=("Helvetica", 25)
        )

        self.__last_save_timestamp = tk.Label(
            info_frame,
            fg=prop("secondaryColor"),
            font=("Helvetica", 11, "bold")
        )

        self.__save_status.grid(row=0, column=0, pady=5)
        self.__last_save_timestamp.grid(row=1, column=0, pady=5)

        info_frame.grid(row=0, column=0, pady=150)

    @staticmethod
    def __get_last_save_info_text(last_save_meta):
        """
        Used to get Google Drive save status label.
        """

        if last_save_meta is None:
            return ""

        time_zone = str(get_localzone())
        date_format = "d MMMM"

        creation_datetime = datetime.strptime(last_save_meta["createdTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        creation_datetime += timezone(time_zone).utcoffset(creation_datetime)

        if creation_datetime.year != date.today().year:
            # Only show year if it's not current one, just to avoid extra information.
            date_format = "d MMMM YYYY"

        creation_date = format_datetime(creation_datetime, date_format, locale=app.state.locale)
        creation_time = creation_datetime.strftime("%H:%M")

        return tr(
            "info_NewestSaveOnDriveInformation",
            creation_date,
            creation_time,
            last_save_meta["owner"]
        )

    @staticmethod
    def __get_last_download_version_text(last_save_meta):
        """
        Used to get local save status label.
        """

        if last_save_meta is None:
            return tr("label_StorageIsEmpty")

        elif app.last_save.identifier is None:
            return tr("label_NoInformationAboutCurrentSaveVersion")

        elif app.last_save.identifier == last_save_meta["name"]:
            return tr("info_SaveIsUpToDate")

        else:
            return tr("info_SaveNeedsToBeDownloaded")
