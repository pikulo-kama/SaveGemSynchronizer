import os
from datetime import datetime
import shutil

from googleapiclient.http import MediaFileUpload

from constants import VALHEIM_SAVES_DIR_ID, VALHEIM_LOCAL_SAVES_DIR, ZIP_EXTENSION, \
    ZIP_MIME_TYPE, PROJECT_ROOT, SAVE_VERSION_FILE_NAME, EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL
from src.core.TextResource import tr
from src.service.gcloud_service import GCloud
from src.gui.popup.notification import Notification
from src.util.file import resolve_output_file, OUTPUT_DIR


class Uploader:

    def __init__(self):
        from src.gui.gui import GUI

        self.__gui = GUI.instance()
        self.__drive = GCloud().get_drive_service()
        self.__filename = f"save-{self.__get_timestamp()}"
        self.__filepath = resolve_output_file(f"{self.__filename}.{ZIP_EXTENSION}")

    def upload(self):

        metadata = {
            "name": f"{self.__filename}.{ZIP_EXTENSION}",
            "parents": [VALHEIM_SAVES_DIR_ID]
        }

        self.__make_archive(self.__filename)
        media = MediaFileUpload(self.__filepath, mimetype=ZIP_MIME_TYPE)

        self.__drive.files().create(
            body=metadata,
            media_body=media,
            fields='id'
        ).execute()

        with open(os.path.join(PROJECT_ROOT, SAVE_VERSION_FILE_NAME), "w") as save_version_file:
            save_version_file.write(metadata["name"])

        self.__gui.trigger_event(EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL)
        Notification(self.__gui).show_notification(tr("notification_SaveHasBeenUploaded"))

    def __make_archive(self, filename):
        shutil.make_archive(resolve_output_file(filename), ZIP_EXTENSION, VALHEIM_LOCAL_SAVES_DIR)

    def __get_timestamp(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    @staticmethod
    def cleanup():
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
