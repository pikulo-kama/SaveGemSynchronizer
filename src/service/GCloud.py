import io
import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from constants import GCLOUD_TOKEN_FILE_NAME, CREDENTIALS_FILE_NAME, ZIP_MIME_TYPE
from src.util.file import resolve_app_data, resolve_project_data, file_name_from_path
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

    @staticmethod
    def query_single(target_field: str, fields: str, q: str):

        try:
            request = GCloud.__drive().files().list(
                q=q,
                spaces="drive",
                fields=fields,
                pageToken=None,
                pageSize=1
            )

            return request.execute().get(target_field)

        except HttpError as e:
            logger.error("Error downloading save metadata", e)
            return None

    @staticmethod
    def download_file(file_id):
        """
        Used to in the first place to download archives.
        """

        request = GCloud.__drive().files().get_media(fileId=file_id)
        file = io.BytesIO()

        downloader = MediaIoBaseDownload(file, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()

        return file.getvalue()

    @staticmethod
    def upload_file(file_path: str, parent_directory_id: str, mime_type=ZIP_MIME_TYPE):
        """
        Used to upload file to google cloud into provided directory.
        """

        media = MediaFileUpload(file_path, mimetype=mime_type)
        metadata = {
            "name": file_name_from_path(file_path),
            "parents": [parent_directory_id]
        }

        try:
            # Upload archive to Google Drive.
            logger.info("Uploading archive to cloud.")
            GCloud.__drive().files().create(
                body=metadata,
                media_body=media,
                fields='id'
            ).execute()

        except HttpError as error:
            logger.error("Error uploading archive to cloud", error)
            raise error

    @staticmethod
    def __drive():
        """
        Used to get raw Google Drive service.
        """
        return build('drive', 'v3', credentials=GCloud.__get_credentials())

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
