import pytest
from unittest.mock import Mock, call
from datetime import datetime

from pytest_mock import MockerFixture

from savegem.common.core.save_meta import SaveMetaProp
from savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind, ProgressEvent
from savegem.common.service.uploader import Uploader
from tests.test_data import PlayerTestData


@pytest.fixture(autouse=True)
def _setup(app_context, user_config_mock, path_exists_mock, resolve_temp_file_mock):
    path_exists_mock.return_value = True
    resolve_temp_file_mock.return_value = "/tmp/test-game-archive"


@pytest.fixture
def mock_game(mocker: MockerFixture):
    """Fixture to create a mock Game object with necessary nested mocks."""
    mock_game = mocker.MagicMock()
    mock_game.name = "TestGame"
    mock_game.local_path = "/path/to/saves"
    mock_game.file_list = ["/path/to/saves/file1.sav", "/path/to/saves/file2.sav"]
    mock_game.metadata_file_path = "/path/to/saves/meta.json"
    mock_game.drive_directory = "Drive/Games/TestGame"

    # Mock metadata calls
    mock_game.meta.local.calculate_checksum.return_value = "NEW_CHECKSUM"
    mock_game.meta.local.checksum = None
    mock_game.meta.local.owner = None
    mock_game.meta.local.created_time = None

    return mock_game


@pytest.fixture
def mock_subscriber():
    """Fixture for a mock subscriber function to check sent events."""
    return Mock()


@pytest.fixture
def uploader(mock_subscriber):
    """Fixture for the Uploader instance with a subscribed mock."""
    uploader = Uploader()
    uploader.subscribe(mock_subscriber)

    return uploader


def test_upload_success(path_exists_mock, resolve_temp_file_mock, makedirs_mock, copy_mock, make_archive_mock,
                        gdrive_mock, datetime_mock, uploader, mock_game, mock_subscriber):
    """Test a successful full upload process, ensuring all 5 stages complete."""

    # Setup datetime
    mock_now = datetime(2025, 10, 2, 12, 30, 0)
    datetime_mock.now.return_value = mock_now

    target_archive_base = "/tmp/test-game-archive"
    target_archive_zip = f"{target_archive_base}.zip"

    # ACT
    uploader.upload(mock_game)

    # ASSERT - Execution Flow (5 stages + DoneEvent)

    # 1. Directory Existence Check
    path_exists_mock.assert_called_with(mock_game.local_path)

    # 2. Stage 1: Target directory creation
    makedirs_mock.assert_called_once_with(target_archive_base)

    # 3. Stage 2: Save files copying
    expected_copy_calls = [
        call(mock_game.file_list[0], target_archive_base),
        call(mock_game.file_list[1], target_archive_base)
    ]
    copy_mock.assert_has_calls(expected_copy_calls, any_order=False)
    assert copy_mock.call_count == 3  # 2 game files + 1 metadata file (later)

    # 4. Stage 3: Metadata update and copy
    mock_game.meta.local.calculate_checksum.assert_called_once()
    assert mock_game.meta.local.checksum == "NEW_CHECKSUM"
    assert mock_game.meta.local.owner == PlayerTestData.FirstPlayerName
    assert mock_game.meta.local.created_time == mock_now.isoformat()
    # Check metadata file copy (the third call to mock_copy)
    assert copy_mock.call_args_list[2] == call(mock_game.metadata_file_path, target_archive_base)

    # 5. Stage 4: Archive creation
    make_archive_mock.assert_called_once_with(
        target_archive_base,
        "zip",
        target_archive_base
    )

    # 6. Stage 5: Upload to Drive
    expected_props = {
        SaveMetaProp.Owner: PlayerTestData.FirstPlayerName,
        SaveMetaProp.Checksum: "NEW_CHECKSUM"
    }
    gdrive_mock.upload_file.assert_called_once()

    # Check upload arguments
    upload_args, upload_kwargs = gdrive_mock.upload_file.call_args
    assert upload_args[0] == target_archive_zip  # file_path
    assert upload_args[1] == mock_game.drive_directory  # drive_directory
    assert upload_kwargs['properties'] == expected_props
    assert 'subscriber' in upload_kwargs  # Check subscriber lambda is passed

    # 7. Final event check
    final_event = mock_subscriber.call_args_list[-1][0][0]
    assert isinstance(final_event, DoneEvent)
    assert final_event.success is True

    # Check the total number of progress calls (5 stages + 0% initial)
    progress_calls = [c for c in mock_subscriber.call_args_list if not isinstance(c[0][0], DoneEvent)]
    assert len(progress_calls) == 5  # 0% + 6 full stage completions -1 since GDrive.upload_file is being mocked.


def test_upload_saves_directory_missing(path_exists_mock, makedirs_mock, uploader, mock_game, mock_subscriber):
    """Test early exit and error handling when the local saves directory is missing."""

    path_exists_mock.return_value = False

    uploader.upload(mock_game)

    # ASSERT - Events Sent (0 Progress and ErrorEvent followed by DoneEvent)
    assert mock_subscriber.call_count == 3

    progress_event = mock_subscriber.call_args_list[0][0][0]
    error_event = mock_subscriber.call_args_list[1][0][0]
    done_event = mock_subscriber.call_args_list[2][0][0]

    assert isinstance(progress_event, ProgressEvent)
    assert progress_event.kind is None
    assert progress_event.progress == 0

    assert isinstance(error_event, ErrorEvent)
    assert error_event.kind == EventKind.SavesDirectoryMissing

    assert isinstance(done_event, DoneEvent)
    assert done_event.success is False
    assert done_event.kind == EventKind.SavesDirectoryMissing

    # ASSERT - Early Exit
    makedirs_mock.assert_not_called()


def test_upload_http_error(module_patch, path_exists_mock, resolve_temp_file_mock, makedirs_mock, copy_mock,
                           make_archive_mock, gdrive_mock, datetime_mock, uploader, mock_game, mock_subscriber,
                           http_error_mock):
    """Test error handling when GDrive.upload_file raises an HttpError."""

    # Setup GDrive mock to raise HttpError
    gdrive_mock.upload_file.side_effect = http_error_mock

    # ACT
    uploader.upload(mock_game)

    # ASSERT - GDrive was called
    gdrive_mock.upload_file.assert_called_once()

    # ASSERT - Events Sent
    # There should be 4 progress calls (0% + 3 completed stages) + ErrorEvent + DoneEvent
    # The error occurs *before* the 5th stage can be fully completed by the subscriber lambda.

    # 1. Check for initial 0% progress + 3 full stage progress calls
    progress_calls = [c for c in mock_subscriber.call_args_list if c[0][0].type == c[0][0].type.Progress]
    assert len(progress_calls) == 5  # 0% + 4 (makedirs, copy files, copy meta, make archive)

    # 2. Check for ErrorEvent and DoneEvent (last two calls)
    error_event = mock_subscriber.call_args_list[-2][0][0]
    done_event = mock_subscriber.call_args_list[-1][0][0]

    assert isinstance(error_event, ErrorEvent)
    assert error_event.kind == EventKind.ErrorUploadingToDrive

    assert isinstance(done_event, DoneEvent)
    assert done_event.success is False
    assert done_event.kind == EventKind.ErrorUploadingToDrive
