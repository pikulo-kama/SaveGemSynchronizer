import os.path
import shutil
from distutils.dir_util import copy_tree

from constants import ZIP_MIME_TYPE, VALHEIM_SAVES_DIR_ID, ZIP_EXTENSION, \
    VALHEIM_LOCAL_SAVES_DIR, PROJECT_ROOT, SAVE_VERSION_FILE_NAME, \
    EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL
from src.core.TextResource import tr
from src.gui.popup.notification import Notification
from src.service.gcloud_service import GCloud
from src.util.file import resolve_output_file


class Downloader:

    def __init__(self):
        from src.gui.gui import GUI

        self.__gui = GUI.instance()
        self.__drive = GCloud().get_drive_service()
        self.__temporary_save_zip_file = f'save.{ZIP_EXTENSION}'

    def download(self):

        save = self.download_last_save()

        if save is None:
            Notification(self.__gui).show_notification(tr("notification_StorageIsEmpty"))
            return

        with open(os.path.join(PROJECT_ROOT, SAVE_VERSION_FILE_NAME), "w") as save_version_file:
            save_version_file.write(save.get("name"))

        # Download file and write it to zip file locally (in output directory)
        file = GCloud().download_file(save.get("id"))
        with open(resolve_output_file(self.__temporary_save_zip_file), "wb") as zip_save:
            zip_save.write(file)

        # Make backup of existing save, just in case
        backup_dir = VALHEIM_LOCAL_SAVES_DIR + "_backup"

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        copy_tree(VALHEIM_LOCAL_SAVES_DIR, backup_dir)

        # Extract archive contents to the target directory
        shutil.unpack_archive(
            resolve_output_file(self.__temporary_save_zip_file),
            VALHEIM_LOCAL_SAVES_DIR,
            ZIP_EXTENSION
        )

        self.__gui.trigger_event(EVENT_UPLOAD_DOWNLOAD_SUCCESSFUL)
        Notification(self.__gui).show_notification(tr("notification_NewSaveHasBeenDownloaded"))

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
