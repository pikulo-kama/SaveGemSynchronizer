import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from constants import GCLOUD_TOKEN_FILE_NAME, SECRET_FILE_NAME, PROJECT_ROOT

SCOPES = [
    'https://www.googleapis.com/auth/docs',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata'
]


class GCloud:

    def get_drive_service(self):
        return build('drive', 'v3', credentials=self.__get_credentials())

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
