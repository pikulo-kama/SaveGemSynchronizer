import io
import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from constants import GCLOUD_TOKEN_FILE_NAME, CREDENTIALS_FILE_NAME
from src.core.holders import game_prop
from src.util.file import resolve_app_data, resolve_project_data
from src.util.logger import get_logger

logger = get_logger(__name__)
SCOPES = [
    'https://www.googleapis.com/auth/docs',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata'
]


class GCloud:
    """
    Class that has most of the Google Cloud interaction logic defined.
    """

    def get_drive_service(self):
        """
        Used to get raw Google Drive service.
        """
        return build('drive', 'v3', credentials=self.__get_credentials())

    def get_last_modified(self, file_id: str):
        """
        Used to get date when file on cloud was modified last time.
        """
        return self.get_file_metadata(file_id, "modifiedTime")["modifiedTime"]

    def get_file_metadata(self, file_id: str, fields: str):
        """
        Used to get file metadata from cloud.
        """
        return self.get_drive_service().files().get(
            fileId=file_id,
            fields=fields
        )

    def download_file_raw(self, file_id: str, mime_type: str):
        """
        Used to download primitive files that could be stored and accessed in-memory.
        """
        return self.get_drive_service().files().export(
            fileId=file_id,
            mimeType=mime_type
        ).execute()

    def download_file(self, file_id):
        """
        Used to in the first place to download archives.
        """

        request = self.get_drive_service().files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        return file.getvalue()

    def get_users(self):
        """
        Used to retrieve user information (name, email) of users that have access to the
        save game parent directory.
        """
        cloud_parent_directory = game_prop("gcloudParentDirectoryId")
        client = self.get_drive_service()

        permissions = client.permissions().list(fileId=cloud_parent_directory).execute()
        users = []

        for permission in permissions["permissions"]:
            users.append(
                client.permissions().get(
                    fileId=cloud_parent_directory,
                    permissionId=permission["id"],
                    fields="emailAddress, displayName"
                ).execute()
            )

        return users

    @staticmethod
    def __get_credentials():
        """
        Used to authenticate to Google Cloud as well as refresh token if needed.
        """

        token_file_name = resolve_app_data(GCLOUD_TOKEN_FILE_NAME)
        credentials_file_name = resolve_project_data(CREDENTIALS_FILE_NAME)
        creds = None

        # Get credentials from file (possible if authentication was done previously)
        if os.path.exists(token_file_name):
            logger.info("Token was found. Application will use credentials from token.")
            creds = Credentials.from_authorized_user_file(token_file_name, SCOPES)

            if creds and creds.valid:
                return creds

        # If they're just expired then try to refresh them
        if creds and creds.expired and creds.refresh_token:
            logger.warn("Credentials expired, performing refresh.")
            creds.refresh(Request())

        # Authenticate with credentials and then store them for future use
        elif os.path.exists(credentials_file_name):
            logger.info("Attempting authentication using credentials.")

            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_name, SCOPES)
            creds = flow.run_local_server(port=0)

            logger.info("Authentication completed.")

            with open(token_file_name, 'w') as token_file:
                logger.info("Saving Google Cloud access token for later use.")
                token_file.write(creds.to_json())

        else:
            logger.fatal("credentials.json is missing.")
            raise RuntimeError("Google Cloud credentials are missing in root of the project. Add credentials.json.")

        return creds
