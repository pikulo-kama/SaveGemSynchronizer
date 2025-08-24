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

SCOPES = [
    'https://www.googleapis.com/auth/docs',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata'
]


class GCloud:

    def get_drive_service(self):
        return build('drive', 'v3', credentials=self.__get_credentials())

    def get_last_modified(self, file_id: str):
        return self.get_file_metadata(file_id, "modifiedTime")["modifiedTime"]

    def get_file_metadata(self, file_id: str, fields: str):
        return self.get_drive_service().files().get(
            fileId=file_id,
            fields=fields
        )

    def download_file_raw(self, file_id: str, mime_type: str):
        return self.get_drive_service().files().export(
            fileId=file_id,
            mimeType=mime_type
        ).execute()

    def download_file(self, file_id):

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

        token_file_name = resolve_app_data(GCLOUD_TOKEN_FILE_NAME)
        secret_file_name = resolve_project_data(CREDENTIALS_FILE_NAME)
        creds = None

        # Get credentials from file (possible if authentication was done previously)
        if os.path.exists(token_file_name):
            creds = Credentials.from_authorized_user_file(token_file_name, SCOPES)

            if creds and creds.valid:
                return creds

        # If they're just expired then try to refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Authenticate with credentials and then store them for future use
        elif os.path.exists(secret_file_name):
            flow = InstalledAppFlow.from_client_secrets_file(secret_file_name, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(token_file_name, 'w') as token_file:
                token_file.write(creds.to_json())

        else:
            raise RuntimeError("Google Cloud credentials are missing in root of the project. Add credentials.json.")

        return creds
