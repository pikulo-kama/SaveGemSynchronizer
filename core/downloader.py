import io
import shutil

from googleapiclient.http import MediaIoBaseDownload

from constants import ZIP_MIME_TYPE, VALHEIM_SAVES_DIR_ID, NOTIFICATION_NO_SAVES_PRESENT_MSG, ZIP_EXTENSION, \
    VALHEIM_LOCAL_SAVES_DIR, NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG
from core import Uploader
from core.gcloud_service import GCloud
from gui.notification import Notification


class Downloader:

    def __init__(self):
        self.__drive = GCloud().get_drive_service()
        self.__temporary_save_zip_file = f'save.{ZIP_EXTENSION}'

    def download(self):

        save = self.__list_saves()

        if len(save) == 0:
            Notification().show_notification(NOTIFICATION_NO_SAVES_PRESENT_MSG)
            return

        save = save[0]
        file_id = save.get("id")

        # Download file and write it to zip file locally (in output directory)
        file = self.__download_file_internal(file_id)

        with open(f"{Uploader.output_dir}/{self.__temporary_save_zip_file}", "wb") as zip_save:
            zip_save.write(file)

        # Extract archive contents to the target directory
        shutil.unpack_archive(
            f"{Uploader.output_dir}/{self.__temporary_save_zip_file}",
            VALHEIM_LOCAL_SAVES_DIR,
            ZIP_EXTENSION
        )

        Notification().show_notification(NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG)

    def __download_file_internal(self, file_id):
        request = self.__drive.files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        return file.getvalue()

    def __list_saves(self):
        page_token = None

        response = self.__drive.files().list(
            q=f"mimeType='{ZIP_MIME_TYPE}' and '{VALHEIM_SAVES_DIR_ID}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        return response.get('files', [])
