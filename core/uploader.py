import os
from datetime import datetime
import shutil

from googleapiclient.http import MediaFileUpload

from constants import VALHEIM_SAVES_DIR_ID, VALHEIM_LOCAL_SAVES_DIR, ZIP_EXTENSION, NOTIFICATION_UPLOAD_COMPLETED_MSG, \
    ZIP_MIME_TYPE, PROJECT_ROOT
from core.gcloud_service import GCloud
from gui.notification import Notification


class Uploader:

    output_dir = os.path.join(PROJECT_ROOT, "output")

    def __init__(self):
        self.__drive = GCloud().get_drive_service()
        self.__filename = f"save-{self.__get_timestamp()}"
        self.__filepath = f"{Uploader.output_dir}/{self.__filename}.{ZIP_EXTENSION}"

    def upload(self):
        return

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

        Notification().show_notification(NOTIFICATION_UPLOAD_COMPLETED_MSG)

    def __make_archive(self, filename):
        shutil.make_archive(f"{Uploader.output_dir}/{filename}", ZIP_EXTENSION, VALHEIM_LOCAL_SAVES_DIR)

    def __get_timestamp(self):
        now = datetime.now()
        return f"{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.month}"

    @staticmethod
    def cleanup():
        for filename in os.listdir(Uploader.output_dir):
            file_path = os.path.join(Uploader.output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
