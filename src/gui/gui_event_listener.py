from constants import EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, EVENT_GAME_SELECTION_CHANGED
from src.core.TextResource import tr
from src.service.downloader import Downloader
from src.util.date import extract_date


class GuiEventListener:

    @staticmethod
    def handle_event(event, gui, context):

        if event == EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL:
            GuiEventListener.update_dynamic_elements(gui)

        elif event == EVENT_GAME_SELECTION_CHANGED:
            GuiEventListener.update_dynamic_elements(gui)

    @staticmethod
    def update_dynamic_elements(gui):
        save = Downloader().download_last_save()
        date_info = extract_date(save["createdTime"])

        gui.save_status.configure(
            text=gui.get_last_download_version_text(save)
        )

        gui.last_save_info.configure(
            text=tr("info_NewestSaveOnCloudInformation", date_info["date"], date_info["time"], save["owner"])
        )
