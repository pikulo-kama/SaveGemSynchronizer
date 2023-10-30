import io
import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from constants import GCLOUD_TOKEN_FILE_NAME, SECRET_FILE_NAME, PROJECT_ROOT, VALHEIM_SAVES_DIR_ID, \
    VALHEIM_XBOX_ACCESS_MAP_FILE_ID

SCOPES = [
    'https://www.googleapis.com/auth/docs',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata'
]


class GCloud:

    def get_drive_service(self):
        return build('drive', 'v3', credentials=self.__get_credentials())

    def download_file(self, file_id):

        request = self.get_drive_service().files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        return file.getvalue()

    def get_users(self):
        client = self.get_drive_service()

        permissions = client.permissions().list(fileId=VALHEIM_SAVES_DIR_ID).execute()
        users = []

        for permission in permissions["permissions"]:
            users.append(
                client.permissions().get(
                    fileId=VALHEIM_SAVES_DIR_ID,
                    permissionId=permission["id"],
                    fields="emailAddress, displayName"
                ).execute()
            )

        return users

    def __get_credentials(self):

        creds = None

        # Get credentials from file (possible if authentication was done previously)
        if os.path.exists(os.path.join(PROJECT_ROOT, GCLOUD_TOKEN_FILE_NAME)):
            creds = Credentials.from_authorized_user_file(os.path.join(PROJECT_ROOT, GCLOUD_TOKEN_FILE_NAME), SCOPES)

        if not creds or not creds.valid:

            # If they're just expired then try to refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else: # Authenticate with credentials and then store them for future use
                flow = InstalledAppFlow.from_client_secrets_file(os.path.join(PROJECT_ROOT, SECRET_FILE_NAME), SCOPES)
                creds = flow.run_local_server(port=0)

                with open(GCLOUD_TOKEN_FILE_NAME, 'w') as token_file:
                    token_file.write(creds.to_json())

        return creds
