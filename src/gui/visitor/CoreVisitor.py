import tkinter as tk

from constants import SAVE_VERSION_FILE_NAME
from src.core.AppState import AppState
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui import GUI, add_button_hover_effect
from src.gui.visitor.Visitor import Visitor
from datetime import date, datetime

from babel.dates import format_datetime
from pytz import timezone
from src.util.file import resolve_app_data
from src.util.logger import get_logger

logger = get_logger(__name__)


class CoreVisitor(Visitor):
    """
    Used to build main application elements.

    Specifically:
    - Last drive save information
    - Local save status information
    - Download/Upload buttons
    - Copyright

    Always enabled.
    """

    def visit(self, gui: GUI):
        self.__add_last_save_info(gui)
        self.__add_buttons_internal(gui)
        self.__add_copyright_and_version(gui)

    def is_enabled(self):
        return True

    def refresh(self, gui: GUI):
        last_save_meta = gui.metadata_function()

        save_status_label = self.__get_last_download_version_text(last_save_meta)
        last_save_info_label = self.__get_last_save_info_text(last_save_meta)

        copy = f"© 2023{"" if date.today().year == 2023 else f"-{date.today().year}"}"
        copyright_label = tr("window_Signature", copy)

        gui.save_status.configure(text=save_status_label)
        logger.debug("Save status label was reloaded. (%s)", save_status_label)

        gui.last_save_info.configure(text=last_save_info_label)
        logger.debug("Last save information label was reloaded. (%s)", last_save_info_label)

        gui.copyright_label.configure(text=copyright_label)
        logger.debug("Copyright was reloaded. (%s)", copyright_label)

        for idx, tk_button in enumerate(gui.tk_buttons):
            name_text_resource = gui.buttons[idx]["nameTextResource"]
            button_label = tr(name_text_resource)

            tk_button.configure(text=button_label)
            logger.debug("Button reloaded (%s)", button_label)

        logger.debug("%d buttons were reloaded.", len(gui.tk_buttons))

    @staticmethod
    def __add_last_save_info(gui):
        """
        Used to render both local and Google Drive save status labels.
        """

        info_frame = tk.Frame(gui.body_frame)

        # Text is empty for fields at this moment
        # They would be populated later by GUI component.
        gui.save_status = tk.Label(
            info_frame,
            fg=prop("primaryColor"),
            font=("Helvetica", 25)
        )

        gui.last_save_info = tk.Label(
            info_frame,
            fg=prop("secondaryColor"),
            font=("Helvetica", 11, "bold")
        )

        gui.save_status.grid(row=0, column=0, pady=5)
        gui.last_save_info.grid(row=1, column=0, pady=5)

        info_frame.grid(row=0, column=0, pady=150)

    @staticmethod
    def __add_buttons_internal(gui):
        """
        Used to render upload and download buttons.
        """

        button_frame = tk.Frame(gui.body_frame)

        for idx, button in enumerate(gui.buttons):
            tk_button = tk.Button(
                button_frame,
                width=button["properties"]["width"],
                command=button["callback"]
            )

            tk_button.grid(row=0, column=idx, padx=5)
            tk_button.config(
                cursor="hand2",
                fg=prop("primaryColor"),
                bg=button["properties"]["colorStatic"],
                borderwidth=0,
                relief=tk.SOLID,
                pady=15,
                padx=15,
                font=40
            )

            add_button_hover_effect(tk_button)
            gui.tk_buttons.insert(idx, tk_button)

        button_frame.grid(row=1, column=0)

    @staticmethod
    def __add_copyright_and_version(gui):
        """
        Used to render copyright label.
        """

        horizontal_frame = tk.Frame(gui.window, pady=-4)

        version_label = tk.Label(horizontal_frame, text=f"v{prop("version")}")
        version_label.grid(row=0, column=0, padx=5)

        gui.copyright_label = tk.Label(horizontal_frame)
        gui.copyright_label.grid(row=0, column=1)

        horizontal_frame.place(relx=.5, rely=.9, anchor=tk.N)

    @staticmethod
    def __get_last_save_info_text(last_save_meta):
        """
        Used to get Google Drive save status label.
        """

        if last_save_meta is None:
            return ""

        locale = AppState.get_locale(prop("defaultLocale"))

        creation_datetime = datetime.strptime(last_save_meta["createdTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        creation_datetime += timezone(prop("timeZone")).utcoffset(creation_datetime)

        creation_date = format_datetime(creation_datetime, "d MMMM", locale=locale)
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

        save_versions = EditableJsonConfigHolder(resolve_app_data(SAVE_VERSION_FILE_NAME))
        last_downloaded_version = save_versions.get_value(AppState.get_game())

        if last_save_meta is None:
            return tr("label_StorageIsEmpty")
            
        elif last_downloaded_version is None:
            return tr("label_NoInformationAboutCurrentSaveVersion")

        elif last_downloaded_version == last_save_meta["name"]:
            return tr("info_SaveIsUpToDate")

        else:
            return tr("info_SaveNeedsToBeDownloaded")
