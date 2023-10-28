from constants import EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL, LAST_SAVE_INFO_LABEL
from core import Downloader


class GuiEventListener:

    def handle_event(self, event, gui, context):

        # If download successful then refresh last save information labels
        if event == EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL:

            save = Downloader().download_last_save()
            date_info = gui.extract_date(save["createdTime"])

            gui.save_status.configure(text=gui.get_last_download_version_text(save))
            gui.last_save_info.configure(
                text=LAST_SAVE_INFO_LABEL.format(date_info["date"], date_info["time"], save["owner"]))
