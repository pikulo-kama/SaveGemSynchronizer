import io
import json
from unittest.mock import Mock

import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _cleanup():
    """
    Ensure GDrive.__drive is reset before each test.
    """

    from savegem.common.service.gdrive import GDrive

    GDrive._GDrive__drive = None


@pytest.fixture
def _drive_service_mock(mocker: MockerFixture):
    """
    Fixture for the mocked Google Drive service object (returned by build).
    """

    mock_service = mocker.MagicMock()

    mock_service.about.return_value \
        .get.return_value \
        .execute.return_value = {"user": {"displayName": "Test User"}}

    # Setup for query_single
    mock_service.files.return_value. \
        list.return_value. \
        execute.return_value = {"files": [{"id": "file_id", "name": "file_name"}]}

    # Setup for get_changes
    mock_service.changes.return_value \
        .getStartPageToken.return_value \
        .execute.return_value = {"startPageToken": "initial_token"}

    mock_service.changes.return_value \
        .list.return_value \
        .execute.return_value = {"changes": [], "newStartPageToken": "new_token"}

    mock_service.permissions.return_value \
        .list.return_value \
        .execute.return_value = {"permissions": [{"user_id": "test"}, {"user_id": "best"}]}

    return mock_service


@pytest.fixture
def mock_creds_valid(mocker: MockerFixture):
    """
    Fixture for a valid (authenticated) Credentials mock.
    """

    mock_creds = mocker.MagicMock(spec=Credentials)
    mock_creds.valid = True

    return mock_creds


@pytest.fixture
def _google_build_mock(module_patch, _drive_service_mock):
    build_mock = module_patch("build")
    build_mock.return_value = _drive_service_mock

    return build_mock


@pytest.fixture
def _installed_app_flow_mock(module_patch):
    return module_patch("InstalledAppFlow")


@pytest.fixture
def _media_file_upload_mock(module_patch):
    return module_patch("MediaFileUpload")


@pytest.fixture
def _media_base_upload_mock(module_patch):
    return module_patch("MediaIoBaseUpload")


@pytest.fixture
def _media_base_download_mock(module_patch):
    return module_patch("MediaIoBaseDownload")


@pytest.fixture
def _credentials_mock(module_patch):
    return module_patch("Credentials", autospec=True)


@pytest.fixture
def _request_mock(module_patch):
    return module_patch("Request")


@pytest.fixture
def _refresh_error_mock(module_patch):
    return module_patch("RefreshError")


@pytest.fixture
def _next_chunk_mock(module_patch):
    return module_patch("GDrive._GDrive__next_chunk")


@pytest.fixture
def _get_creds_mock(module_patch):
    return module_patch("GDrive._GDrive__get_credentials")


def test_get_credentials_from_token_file(resolve_project_data_mock, resolve_app_data_mock, _credentials_mock,
                                         path_exists_mock, mock_creds_valid, _google_build_mock):
    """
    Test successful authentication using an existing valid token file.
    """

    from savegem.common.service.gdrive import GDrive, GDRIVE_SCOPES

    resolve_app_data_mock.return_value = "token.json"
    resolve_project_data_mock.return_value = "creds.json"
    path_exists_mock.side_effect = [True, True]

    _credentials_mock.from_authorized_user_file.return_value = mock_creds_valid

    GDrive.get_current_user()

    # Assert
    _credentials_mock.from_authorized_user_file.assert_called_once_with("token.json", GDRIVE_SCOPES)
    assert mock_creds_valid.valid is True


def test_get_current_user(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """
    Test get_current_user calls the correct Drive API endpoint.
    """

    from savegem.common.service.gdrive import GDrive

    user_info = GDrive.get_current_user()

    # Assert
    _drive_service_mock.about().get.assert_called_once_with(fields="user")
    assert user_info == {"displayName": "Test User"}


def test_get_users_with_access(_google_build_mock, _drive_service_mock, _get_creds_mock):

    from savegem.common.service.gdrive import GDrive

    file_id = "test"
    result = GDrive.get_users_with_access(file_id)

    _drive_service_mock.permissions.return_value.list.assert_called_once_with(
        fileId=file_id,
        fields="permissions(id, emailAddress, displayName, photoLink)"
    )

    assert result == [{"user_id": "test"}, {"user_id": "best"}]


def test_query_metadata_success(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """
    Test query_metadata successful execution.
    """

    from savegem.common.service.gdrive import GDrive

    page_size = 123
    q_str = "name='test'"
    fields_str = "files(id, name)"

    result = GDrive.query_metadata(q_str, fields_str, page_size)

    # Assert
    _drive_service_mock.files.return_value.list.assert_called_once_with(
        q=q_str,
        spaces="drive",
        fields=fields_str,
        pageToken=None,
        pageSize=page_size
    )
    assert result == {"files": [{"id": "file_id", "name": "file_name"}]}


def test_query_metadata_http_error(logger_mock, http_error_mock, _google_build_mock, _drive_service_mock,
                                 _get_creds_mock):
    """
    Test query_metadata handling of HttpError.
    """

    from savegem.common.service.gdrive import GDrive

    # Setup mock to raise HttpError
    _drive_service_mock.files.return_value \
        .list.return_value \
        .execute.side_effect = http_error_mock

    result = GDrive.query_metadata("q", "f")

    assert result is None


def test_next_chunk_progress():
    """
    Test __next_chunk correctly calculates and calls subscriber with progress.
    """

    from savegem.common.service.gdrive import GDrive

    mock_request = Mock()
    mock_subscriber = Mock()

    # Setup: Not done, status available
    mock_status = Mock()
    mock_status.progress.return_value = 0.75
    mock_request.next_chunk.return_value = (mock_status, False)

    # Act
    GDrive._GDrive__next_chunk(mock_request, mock_subscriber)  # noqa

    # Assert
    mock_request.next_chunk.assert_called_once()
    mock_status.progress.assert_called_once()
    mock_subscriber.assert_called_once_with(0.75)


def test_next_chunk_done():
    """
    Test __next_chunk calls subscriber with 1.0 when done.
    """

    from savegem.common.service.gdrive import GDrive

    mock_request = Mock()
    mock_subscriber = Mock()

    # Setup: Done
    mock_request.next_chunk.return_value = (None, True)

    # Act
    GDrive._GDrive__next_chunk(mock_request, mock_subscriber)  # noqa

    # Assert
    mock_subscriber.assert_called_once_with(1)


def test_next_chunk_no_status():
    """
    Test __next_chunk calls subscriber with 0 when status is None (and not done).
    """

    from savegem.common.service.gdrive import GDrive

    mock_request = Mock()
    mock_subscriber = Mock()

    # Setup: Not done, status None (should trigger progress = 0)
    mock_request.next_chunk.return_value = (None, False)

    # Act
    GDrive._GDrive__next_chunk(mock_request, mock_subscriber)  # noqa

    # Assert
    mock_subscriber.assert_called_once_with(0)


def test_next_chunk_no_subscriber():
    """
    Test __next_chunk does nothing if no subscriber provided.
    """

    from savegem.common.service.gdrive import GDrive

    mock_request = Mock()

    # Setup
    mock_request.next_chunk.return_value = (Mock(), False)

    # Act
    status, done = GDrive._GDrive__next_chunk(mock_request, None)  # noqa

    # Assert
    mock_request.next_chunk.assert_called_once()


def test_download_file_success(_google_build_mock, _next_chunk_mock, _media_base_download_mock, _drive_service_mock,
                               _get_creds_mock):
    """
    Test download_file successful completion.
    """

    from savegem.common.service.gdrive import GDrive

    file_id = "test_id"

    # Setup: 2 chunks (False, False) followed by done (None, True)
    _next_chunk_mock.side_effect = [
        (Mock(), False),
        (Mock(), False),
        (None, True)
    ]

    # Act
    file_io = GDrive.download_file(file_id, subscriber=Mock())

    # Assert
    _drive_service_mock.files().get_media.assert_called_once_with(fileId=file_id)
    _media_base_download_mock.assert_called_once()
    assert _next_chunk_mock.call_count == 3
    assert isinstance(file_io, io.BytesIO)


def test_download_file_http_error(_google_build_mock, _next_chunk_mock, _media_base_download_mock, http_error_mock,
                                  _get_creds_mock):
    """
    Test download_file handles HttpError.
    """

    from savegem.common.service.gdrive import GDrive

    file_id = "test_id"

    _next_chunk_mock.side_effect = http_error_mock

    file_io = GDrive.download_file(file_id)

    assert file_io is None


def test_upload_file_success(_google_build_mock, _next_chunk_mock, _media_file_upload_mock,
                             file_name_from_path_mock, _drive_service_mock, _get_creds_mock):
    """
    Test upload_file successful completion.
    """

    from constants import ZIP_MIME_TYPE
    from savegem.common.service.gdrive import GDrive

    file_name_from_path_mock.return_value = "test.zip"

    # Setup: 2 chunks followed by done
    _next_chunk_mock.side_effect = [(Mock(), False), (Mock(), False), (None, True)]

    file_path = "/tmp/test.zip"
    parent_id = "parent_folder"
    props = {"prop_key": "prop_val"}

    # Act
    GDrive.upload_file(file_path, parent_id, properties=props)

    # Assert
    _media_file_upload_mock.assert_called_once_with(
        file_path,
        mimetype=ZIP_MIME_TYPE,
        resumable=True,
        chunksize=GDrive.ChunkSize
    )

    expected_metadata = {
        "name": "test.zip",
        "parents": [parent_id],
        "appProperties": props
    }

    _drive_service_mock.files().create.assert_called_once_with(
        body=expected_metadata,
        media_body=_media_file_upload_mock.return_value,
        fields="id"
    )
    assert _next_chunk_mock.call_count == 3


def test_upload_file_http_error(_google_build_mock, http_error_mock, _next_chunk_mock, _media_file_upload_mock,
                                file_name_from_path_mock, _get_creds_mock):
    """
    Test upload_file handles HttpError by raising it.
    """

    from savegem.common.service.gdrive import GDrive

    file_name_from_path_mock.return_value = "test.zip"

    # Setup: HttpError occurs on the first chunk
    _next_chunk_mock.side_effect = http_error_mock

    # Act & Assert
    with pytest.raises(HttpError):
        GDrive.upload_file("/tmp/test.zip", "parent_id")


def test_update_file_success(_google_build_mock, _next_chunk_mock, _media_base_upload_mock, _drive_service_mock,
                             _get_creds_mock):
    """
    Test update_file successful completion.
    """

    from savegem.common.service.gdrive import GDrive

    # Setup: 2 chunks followed by done
    _next_chunk_mock.side_effect = [(Mock(), False), (Mock(), False), (None, True)]

    file_id = "meta_id"
    data = '{"key": "value"}'

    # Act
    GDrive.update_file(file_id, data)

    # Assert
    _media_base_upload_mock.assert_called_once()

    _drive_service_mock.files().update.assert_called_once_with(
        fileId=file_id,
        media_body=_media_base_upload_mock.return_value
    )
    assert _next_chunk_mock.call_count == 3


def test_update_file_http_error(_google_build_mock, _next_chunk_mock, _media_base_upload_mock, http_error_mock,
                                _get_creds_mock):
    """
    Test update_file handles HttpError by raising it.
    """

    from savegem.common.service.gdrive import GDrive

    _next_chunk_mock.side_effect = http_error_mock

    # Act & Assert
    with pytest.raises(HttpError):
        GDrive.update_file("meta_id", "data")


def test_get_changes_no_start_token(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """
    Test get_changes fetches start token if none is provided.
    """

    from savegem.common.service.gdrive import GDrive

    # Act
    result = GDrive.get_changes(None)

    # Assert: Should first call getStartPageToken
    _drive_service_mock.changes().getStartPageToken().execute.assert_called_once()

    # Assert: Then call list
    _drive_service_mock.changes().list.assert_called_once_with(
        pageToken="initial_token",
        fields="changes(file(id, name, parents), removed), newStartPageToken"
    )
    assert result == {"changes": [], "newStartPageToken": "new_token"}


def test_get_changes_with_start_token(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """
    Test get_changes uses provided start token.
    """

    from savegem.common.service.gdrive import GDrive

    start_token = "provided_token"

    # Act
    result = GDrive.get_changes(start_token)

    # Assert: Should NOT call getStartPageToken
    _drive_service_mock.changes().getStartPageToken().execute.assert_not_called()

    # Assert: Should call list with provided token
    _drive_service_mock.changes().list.assert_called_once_with(
        pageToken=start_token,
        fields="changes(file(id, name, parents), removed), newStartPageToken"
    )
    assert result == {"changes": [], "newStartPageToken": "new_token"}


def test_valid_credentials_found(_credentials_mock, logger_mock, resolve_app_data_mock):
    """
    Tests the case where valid credentials are loaded from the file.
    """

    from constants import File
    from savegem.common.service.gdrive import GDRIVE_SCOPES, GDrive

    resolve_app_data_mock.return_value = File.GDriveToken
    creds_mock = _credentials_mock.from_authorized_user_file.return_value
    creds_mock.valid = True
    creds_mock.expired = False

    result = GDrive._GDrive__get_credentials()  # noqa

    assert result == creds_mock
    creds_mock.refresh.assert_not_called()

    logger_mock.info.assert_called_with("Token was found. Application will use credentials from token.")
    _credentials_mock.from_authorized_user_file.assert_called_once_with(
        File.GDriveToken, GDRIVE_SCOPES
    )


def test_expired_credentials_refresh_successful(_credentials_mock, logger_mock, resolve_app_data_mock, _request_mock):
    """
    Tests the case where expired credentials are successfully refreshed.
    """

    from constants import File
    from savegem.common.service.gdrive import GDrive

    resolve_app_data_mock.return_value = File.GDriveToken
    creds_mock = _credentials_mock.from_authorized_user_file.return_value
    creds_mock.refresh_token = 'valid_refresh_token'
    creds_mock.valid = False
    creds_mock.expired = True

    result = GDrive._GDrive__get_credentials()  # noqa

    assert result == creds_mock
    # Verify refresh was called exactly once with the mocked Request object
    creds_mock.refresh.assert_called_once_with(_request_mock.return_value)

    # Verify correct logging
    logger_mock.info.assert_called_with("Credentials expired, performing refresh.")
    assert logger_mock.info.call_count == 2  # Initial token found + refresh info


def test_expired_credentials_refresh_failed(_credentials_mock, logger_mock, resolve_app_data_mock, _request_mock):
    """
    Tests the case where the refresh fails due to an expired refresh token.
    """

    from constants import File
    from savegem.common.service.gdrive import GDrive

    resolve_app_data_mock.return_value = File.GDriveToken
    creds_mock = _credentials_mock.from_authorized_user_file.return_value
    creds_mock.refresh_token = "expired_refresh_token"
    creds_mock.valid = False
    creds_mock.expired = True

    # Set the side effect to simulate refresh failure
    creds_mock.refresh.side_effect = RefreshError("Token revoked.")

    result = GDrive._GDrive__get_credentials()  # noqa

    assert result == creds_mock
    creds_mock.refresh.assert_called_once()
    logger_mock.error.assert_called_with("Refresh token expired. Starting authentication process.")


def test_is_authenticated_true(path_exists_mock, resolve_app_data_mock):
    """
    Tests when the token file exists.
    """

    from savegem.common.service.gdrive import GoogleAuth

    path_exists_mock.return_value = True
    resolve_app_data_mock.return_value = "/fake/app/token.json"

    assert GoogleAuth.is_authenticated() is True


def test_is_authenticated_false(path_exists_mock, resolve_app_data_mock):
    """
    Tests when the token file does not exist.
    """

    from savegem.common.service.gdrive import GoogleAuth

    path_exists_mock.return_value = False
    resolve_app_data_mock.return_value = "/fake/app/token.json"

    assert GoogleAuth.is_authenticated() is False


def test_authenticate_skip_if_token_exists(logger_mock, path_exists_mock, _installed_app_flow_mock):
    """
    Tests that authentication is skipped if the token file already exists.
    """

    from savegem.common.service.gdrive import GoogleAuth

    path_exists_mock.side_effect = [True, False]

    GoogleAuth.authenticate()

    logger_mock.info.assert_called_with("Skipping authentication. User is already authenticated.")
    _installed_app_flow_mock.from_client_secrets_file.assert_not_called()


def test_authenticate_raises_if_creds_missing(logger_mock, path_exists_mock):
    """
    Tests that a RuntimeError is raised if the credentials file is missing.
    """

    from constants import File
    from savegem.common.service.gdrive import GoogleAuth

    path_exists_mock.side_effect = [False, False]

    with pytest.raises(RuntimeError) as error:
        GoogleAuth.authenticate()

    assert f"Google Cloud credentials are missing" in str(error.value)
    logger_mock.critical.assert_called_with(f"{File.GDriveCreds} is missing.")


def test_authenticate_success(logger_mock, save_file_mock, path_exists_mock, resolve_app_data_mock,
                              resolve_project_data_mock, _installed_app_flow_mock):
    """
    Tests the full authentication flow, saving the new token.
    """

    from savegem.common.service.gdrive import GoogleAuth, GDRIVE_SCOPES

    mock_creds_json = {"token": "mock_access_token", "refresh_token": "mock_refresh"}
    token_path = '/fake/app/token.json'
    creds_path = '/fake/project/creds.json'

    resolve_app_data_mock.return_value = token_path
    resolve_project_data_mock.return_value = creds_path
    path_exists_mock.side_effect = [False, True]

    mock_flow = _installed_app_flow_mock.from_client_secrets_file.return_value
    mock_creds = mock_flow.run_local_server.return_value

    mock_creds.to_json.return_value = json.dumps(mock_creds_json)

    GoogleAuth.authenticate()

    # Verify the flow was initiated correctly
    _installed_app_flow_mock.from_client_secrets_file.assert_called_once_with(
        creds_path, GDRIVE_SCOPES
    )
    mock_flow.run_local_server.assert_called_once()

    logger_mock.info.assert_any_call("Attempting authentication using credentials.")
    logger_mock.info.assert_called_with("Saving Google Cloud access token for later use.")

    save_file_mock.assert_called_once_with(
        token_path,
        mock_creds_json,  # The result of json.loads(creds.to_json())
        as_json=True
    )
