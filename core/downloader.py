import io
import os.path
import shutil

from googleapiclient.http import MediaIoBaseDownload

from constants import ZIP_MIME_TYPE, VALHEIM_SAVES_DIR_ID, NOTIFICATION_NO_SAVES_PRESENT_MSG, ZIP_EXTENSION, \
    VALHEIM_LOCAL_SAVES_DIR, NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG, PROJECT_ROOT, SAVE_VERSION_FILE_NAME, \
    EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL
from core import Uploader
from core.gcloud_service import GCloud
from gui.popup.notification import Notification


class Downloader:

    def __init__(self, gui):
        self.__gui = gui
        self.__drive = GCloud().get_drive_service()
        self.__temporary_save_zip_file = f'save.{ZIP_EXTENSION}'

    def download(self):

        save = self.download_last_save()

        if save is None:
            Notification(self.__gui).show_notification(NOTIFICATION_NO_SAVES_PRESENT_MSG)
            return

        with open(os.path.join(PROJECT_ROOT, SAVE_VERSION_FILE_NAME), "w") as save_version_file:
            save_version_file.write(save.get("name"))

        # Download file and write it to zip file locally (in output directory)
        file = self.__download_file_internal(save.get("id"))
        with open(f"{Uploader.output_dir}/{self.__temporary_save_zip_file}", "wb") as zip_save:
            zip_save.write(file)

        # Extract archive contents to the target directory
        shutil.unpack_archive(
            f"{Uploader.output_dir}/{self.__temporary_save_zip_file}",
            VALHEIM_LOCAL_SAVES_DIR,
            ZIP_EXTENSION
        )

        self.__gui.trigger_event(EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL)
        Notification(self.__gui).show_notification(NOTIFICATION_DOWNLOAD_AND_EXTRACT_COMPLETE_MSG)

    def __download_file_internal(self, file_id):
        request = self.__drive.files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        return file.getvalue()

    def download_last_save(self):
        page_token = None

        response = self.__drive.files().list(
            q=f"mimeType='{ZIP_MIME_TYPE}' and '{VALHEIM_SAVES_DIR_ID}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, owners, createdTime)',
            pageToken=page_token,
            pageSize=1
        ).execute()

        save = None

        if len(response.get('files', [])) == 1:
            save = response.get('files', [])[0]
            save["owner"] = save["owners"][0]["displayName"]
            del save["owners"]

        return save
