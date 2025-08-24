from constants import EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, EVENT_GAME_SELECTION_CHANGED
from src.core.TextResource import tr
from src.gui.gui import GUI
from src.gui.popup.notification import notification
from src.util.date import extract_date


def trigger_event(event: str, context=None):
    GuiEventListener.handle_event(event, GUI.instance(), context)


class GuiEventListener:

    @staticmethod
    def handle_event(event, gui, context):

        if event == EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL:
            GuiEventListener.update_dynamic_elements(gui, context)

        elif event == EVENT_GAME_SELECTION_CHANGED:
            GuiEventListener.update_dynamic_elements(gui, context)

    @staticmethod
    def update_dynamic_elements(gui, save_meta):

        last_save_info_label = ""

        if save_meta is not None:
            date_info = extract_date(save_meta["createdTime"])
            last_save_info_label = tr(
                "info_NewestSaveOnCloudInformation",
                date_info["date"],
                date_info["time"],
                save_meta["owner"]
            )

        gui.save_status.configure(
            text=gui.get_last_download_version_text(save_meta)
        )

        gui.last_save_info.configure(
            text=last_save_info_label
        )
