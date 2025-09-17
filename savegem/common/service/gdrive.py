import io
import json
import logging
import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload

from constants import ZIP_MIME_TYPE, JSON_MIME_TYPE, File, UTF_8
from savegem.common.util.file import resolve_app_data, resolve_project_data, file_name_from_path, save_file
from savegem.common.util.logger import get_logger
from savegem.common.util.timer import measure_time

_logger = get_logger(__name__)
_SCOPES = [
    "https://www.googleapis.com/auth/docs",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.appdata"
]


class GDrive:
    """
    Class that has most of the Google Drive interaction logic defined.
    """

    __CHUNK_SIZE = 10 * 1024 * 1024

    @staticmethod
    def get_current_user():
        """
        Used to get information about authenticated user.
        """
        response = GDrive.__drive().about() \
            .get(fields="user") \
            .execute()

        return response.get("user")

    @staticmethod
    def query_single(q: str, fields: str):
        """
        Used to query metadata of single file from Google Drive.
        """

        try:
            return GDrive.__drive().files().list(
                q=q,
                spaces="drive",
                fields=fields,
                pageToken=None,
                pageSize=1
            ).execute()

        except HttpError as e:
            _logger.error("Error querying file metadata", e)
            return None

    @staticmethod
    @measure_time(when=logging.DEBUG)
    def download_file(file_id, subscriber=None):
        """
        Used to in the first place to download archives.
        """

        done = False
        file = io.BytesIO()
        request = GDrive.__drive().files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(file, request, chunksize=GDrive.__CHUNK_SIZE)

        try:
            while not done:
                _, done = GDrive.__next_chunk(downloader, subscriber)

        except HttpError as error:
            _logger.error("Failed to download file from drive", error)
            return None
        
        return file

    @staticmethod
    @measure_time(when=logging.DEBUG)
    def upload_file(file_path: str, parent_directory_id: str, mime_type=ZIP_MIME_TYPE,
                    properties: dict = None, subscriber=None):
        """
        Used to upload file to Google Drive into provided directory.
        """

        done = False
        media = MediaFileUpload(
            file_path,
            mimetype=mime_type,
            resumable=True,
            chunksize=GDrive.__CHUNK_SIZE
        )
        metadata = {
            "name": file_name_from_path(file_path),
            "parents": [parent_directory_id],
            "appProperties": properties
        }

        try:
            request = GDrive.__drive().files().create(
                body=metadata,
                media_body=media,
                fields="id"
            )

            while not done:
                _, done = GDrive.__next_chunk(request, subscriber)

        except HttpError as error:
            _logger.error("Error uploading file to drive", error)
            raise error

    @staticmethod
    def update_file(file_id: str, data: str, mime_type=JSON_MIME_TYPE, subscriber=None):
        """
        Used to update existing file in Google Drive.
        """

        done = False
        bytes_io = io.BytesIO(data.encode(UTF_8))
        media = MediaIoBaseUpload(bytes_io, mime_type, resumable=True)

        try:
            request = GDrive.__drive().files().update(
                fileId=file_id,
                media_body=media
            )

            while not done:
                _, done = GDrive.__next_chunk(request, subscriber)

        except HttpError as error:
            _logger.error("Error updating file in drive", error)
            raise error

    @staticmethod
    def get_start_page_token():
        """
        Used to get start page token to query Google Drive Changes API.
        """
        return

    @staticmethod
    def get_changes(start_page_token):
        """
        Used to get changes from specified.
        Start page token used to specify starting point
        of changes that needs to be retrieved.
        """

        if start_page_token is None:
            start_page_token = GDrive.__drive().changes() \
                .getStartPageToken() \
                .execute() \
                .get("startPageToken")

        return GDrive.__drive().changes().list(
            pageToken=start_page_token,
            fields="changes(file(id, name, parents), removed), newStartPageToken"
        ).execute()

    @staticmethod
    def __next_chunk(request, subscriber=None):
        """
        Wrapper method which formats progress into percentage number from 0 to 100.
        Accepts subscriber callback which could be used to respond to download/upload progress.
        """

        status, done = request.next_chunk()

        if subscriber is not None:

            if done:
                progress = 1
            elif status is not None:
                progress = status.progress()
            else:
                progress = 0

            subscriber(progress)

        return status, done

    @staticmethod
    def __drive():
        """
        Used to get raw Google Drive service.
        """
        return build("drive", "v3", credentials=GDrive.__get_credentials())

    @staticmethod
    def __get_credentials():
        """
        Used to authenticate to Google Cloud as well as refresh token if needed.
        """

        token_file_name = resolve_app_data(File.GDriveToken)
        credentials_file_name = resolve_project_data(File.GDriveCreds)
        creds = None

        # Get credentials from file (possible if authentication was done previously)
        if os.path.exists(token_file_name):
            _logger.debug("Token was found. Application will use credentials from token.")
            creds = Credentials.from_authorized_user_file(token_file_name, _SCOPES)

            if creds and creds.valid:
                return creds

        # If they're just expired then try to refresh them
        if creds and creds.expired and creds.refresh_token:
            _logger.debug("Credentials expired, performing refresh.")
            creds.refresh(Request())

        # Authenticate with credentials and then store them for future use
        elif os.path.exists(credentials_file_name):
            _logger.debug("Attempting authentication using credentials.")

            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_name, _SCOPES)
            creds = flow.run_local_server(port=0)

            _logger.debug("Authentication completed.")
            _logger.debug("Saving Google Cloud access token for later use.")
            save_file(token_file_name, json.loads(creds.to_json()), as_json=True)

        else:
            _logger.critical(f"{File.GDriveCreds} is missing.")
            raise RuntimeError(f"Google Cloud credentials are missing in root of the project. Add {File.GDriveCreds}.")

        return creds
