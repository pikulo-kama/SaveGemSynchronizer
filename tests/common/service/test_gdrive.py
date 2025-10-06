import io
from unittest.mock import Mock

import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from pytest_mock import MockerFixture

from constants import ZIP_MIME_TYPE
from savegem.common.service.gdrive import GDrive, GDRIVE_SCOPES


@pytest.fixture(autouse=True)
def reset_gdrive_class():
    """Ensure GDrive.__drive is reset before each test."""
    GDrive._GDrive__drive = None


@pytest.fixture
def _drive_service_mock(mocker: MockerFixture):
    """Fixture for the mocked Google Drive service object (returned by build)."""

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
    """Test successful authentication using an existing valid token file."""

    resolve_app_data_mock.return_value = "token.json"
    resolve_project_data_mock.return_value = "creds.json"
    path_exists_mock.side_effect = [True, True]

    _credentials_mock.from_authorized_user_file.return_value = mock_creds_valid

    GDrive.get_current_user()

    # Assert
    _credentials_mock.from_authorized_user_file.assert_called_once_with("token.json", GDRIVE_SCOPES)
    assert mock_creds_valid.valid is True


def test_get_credentials_from_flow(_google_build_mock, resolve_project_data_mock, resolve_app_data_mock,
                                   path_exists_mock, _installed_app_flow_mock, json_mock, save_file_mock,
                                   mock_creds_valid):
    """Test successful authentication using client secrets file (new flow)."""

    path_exists_mock.side_effect = [False, True]

    resolve_app_data_mock.return_value = "token.json"
    resolve_project_data_mock.return_value = "creds.json"

    # Setup Flow
    mock_flow = Mock()
    mock_flow.run_local_server.return_value = mock_creds_valid
    mock_creds_valid.to_json.return_value = '{"token": "new"}'
    _installed_app_flow_mock.from_client_secrets_file.return_value = mock_flow

    GDrive.get_current_user()

    # Assert
    _installed_app_flow_mock.from_client_secrets_file.assert_called_once_with("creds.json", GDRIVE_SCOPES)
    mock_flow.run_local_server.assert_called_once()
    save_file_mock.assert_called_once()


def test_get_credentials_refresh_expired(path_exists_mock, _credentials_mock, _request_mock,
                                         mock_creds_valid, _google_build_mock):
    """Test refreshing expired credentials."""

    path_exists_mock.side_effect = [True, False]

    mock_creds_valid.valid = False
    mock_creds_valid.expired = True
    mock_creds_valid.refresh_token = True

    _credentials_mock.from_authorized_user_file.return_value = mock_creds_valid

    GDrive.get_current_user()

    mock_creds_valid.refresh.assert_called_once()


def test_should_handle_refresh_error_silently(path_exists_mock, _credentials_mock, _request_mock,
                                              mock_creds_valid, _google_build_mock, logger_mock):
    """Test refreshing expired credentials."""

    path_exists_mock.side_effect = [True, False]

    mock_creds_valid.valid = False
    mock_creds_valid.expired = True
    mock_creds_valid.refresh_token = True
    mock_creds_valid.refresh.side_effect = RefreshError

    _credentials_mock.from_authorized_user_file.return_value = mock_creds_valid

    with pytest.raises(RuntimeError):
        GDrive.get_current_user()

    logger_mock.error.assert_called_once()


def test_get_credentials_missing_all(path_exists_mock):
    """Test raises RuntimeError when both token and creds files are missing."""

    path_exists_mock.side_effect = [False, False]

    with pytest.raises(RuntimeError):
        GDrive._GDrive__get_credentials()  # noqa


def test_get_current_user(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """Test get_current_user calls the correct Drive API endpoint."""

    user_info = GDrive.get_current_user()

    # Assert
    _drive_service_mock.about().get.assert_called_once_with(fields="user")
    assert user_info == {"displayName": "Test User"}


def test_query_single_success(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """Test query_single successful execution."""

    q_str = "name='test'"
    fields_str = "files(id, name)"

    result = GDrive.query_single(q_str, fields_str)

    # Assert
    _drive_service_mock.files().list.assert_called_once_with(
        q=q_str,
        spaces="drive",
        fields=fields_str,
        pageToken=None,
        pageSize=1
    )
    assert result == {"files": [{"id": "file_id", "name": "file_name"}]}


def test_query_single_http_error(logger_mock, http_error_mock, _google_build_mock, _drive_service_mock,
                                 _get_creds_mock):
    """Test query_single handling of HttpError."""

    # Setup mock to raise HttpError
    _drive_service_mock.files().list().execute.side_effect = http_error_mock

    result = GDrive.query_single("q", "f")

    assert result is None


def test_next_chunk_progress():
    """Test __next_chunk correctly calculates and calls subscriber with progress."""
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
    """Test __next_chunk calls subscriber with 1.0 when done."""
    mock_request = Mock()
    mock_subscriber = Mock()

    # Setup: Done
    mock_request.next_chunk.return_value = (None, True)

    # Act
    GDrive._GDrive__next_chunk(mock_request, mock_subscriber)  # noqa

    # Assert
    mock_subscriber.assert_called_once_with(1)


def test_next_chunk_no_status():
    """Test __next_chunk calls subscriber with 0 when status is None (and not done)."""
    mock_request = Mock()
    mock_subscriber = Mock()

    # Setup: Not done, status None (should trigger progress = 0)
    mock_request.next_chunk.return_value = (None, False)

    # Act
    GDrive._GDrive__next_chunk(mock_request, mock_subscriber)  # noqa

    # Assert
    mock_subscriber.assert_called_once_with(0)


def test_next_chunk_no_subscriber():
    """Test __next_chunk does nothing if no subscriber provided."""
    mock_request = Mock()

    # Setup
    mock_request.next_chunk.return_value = (Mock(), False)

    # Act
    status, done = GDrive._GDrive__next_chunk(mock_request, None)  # noqa

    # Assert
    mock_request.next_chunk.assert_called_once()


def test_download_file_success(_google_build_mock, _next_chunk_mock, _media_base_download_mock, _drive_service_mock,
                               _get_creds_mock):
    """Test download_file successful completion."""
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
    """Test download_file handles HttpError."""
    file_id = "test_id"

    # Setup: HttpError occurs on the first chunk
    _next_chunk_mock.side_effect = http_error_mock

    # Act
    file_io = GDrive.download_file(file_id)

    # Assert
    assert file_io is None
    # Check error logging (implicit via mock_logger)


def test_upload_file_success(_google_build_mock, _next_chunk_mock, _media_file_upload_mock,
                             file_name_from_path_mock, _drive_service_mock, _get_creds_mock):
    """Test upload_file successful completion."""

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
    """Test upload_file handles HttpError by raising it."""

    file_name_from_path_mock.return_value = "test.zip"

    # Setup: HttpError occurs on the first chunk
    _next_chunk_mock.side_effect = http_error_mock

    # Act & Assert
    with pytest.raises(HttpError):
        GDrive.upload_file("/tmp/test.zip", "parent_id")


def test_update_file_success(_google_build_mock, _next_chunk_mock, _media_base_upload_mock, _drive_service_mock,
                             _get_creds_mock):
    """Test update_file successful completion."""

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
    """Test update_file handles HttpError by raising it."""

    _next_chunk_mock.side_effect = http_error_mock

    # Act & Assert
    with pytest.raises(HttpError):
        GDrive.update_file("meta_id", "data")


def test_get_changes_no_start_token(_google_build_mock, _drive_service_mock, _get_creds_mock):
    """Test get_changes fetches start token if none is provided."""

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
    """Test get_changes uses provided start token."""

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
