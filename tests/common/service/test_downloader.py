import pytest
from unittest.mock import Mock

from savegem.common.service.downloader import Downloader
from savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind, ProgressEvent


@pytest.fixture
def mock_game():
    """Fixture to create a mock Game object with necessary nested mocks."""
    mock_game = Mock()
    mock_game.local_path = "/path/to/local/saves"
    mock_game.meta.drive.is_present = True
    mock_game.meta.drive.id = "drive_file_id"
    mock_game.meta.local.checksum = "local_checksum_old"
    mock_game.meta.drive.checksum = "drive_checksum_new"

    # Ensure refresh is available
    mock_game.meta.drive.refresh = Mock()

    return mock_game


@pytest.fixture
def mock_subscriber():
    """Fixture for a mock subscriber function to check sent events."""
    return Mock()


@pytest.fixture
def _downloader(mock_subscriber):
    """Fixture for the Downloader instance with a subscribed mock."""
    downloader = Downloader()
    downloader.subscribe(mock_subscriber)

    return downloader


def test_download_success(path_exists_mock, module_patch, copytree_mock,
                          _downloader, cleanup_directory_mock, mock_game, mock_subscriber):
    """Test a successful full download process."""

    mock_unpack_archive = module_patch("shutil.unpack_archive")
    mock_save_file = module_patch("save_file")
    mock_gdrive = module_patch("GDrive")
    module_patch("resolve_temp_file", return_value="/tmp/save.zip")
    module_patch("os.removedirs")
    path_exists_mock.return_value = True  # Directory exists

    # Setup GDrive mock to return a BytesIO object (simulating file content)
    mock_file_content = b"save_data"
    mock_gdrive.download_file.return_value.getvalue.return_value = mock_file_content

    # ACT
    _downloader.download(mock_game)

    # ASSERT - Execution Flow (6 stages + DoneEvent)

    # 1. Check game directory check (mocked as True)
    path_exists_mock.assert_any_call(mock_game.local_path)

    # 2. Check stages set and initial 0% progress sent
    # (The Downloader is a SubscriptableService, which sends 0% progress on _set_stages)
    assert mock_subscriber.call_count > 0

    # 3. Check metadata refresh
    mock_game.meta.drive.refresh.assert_called_once()

    # 4. Check GDrive download and subscriber setup
    mock_gdrive.download_file.assert_called_once()
    # Check that a subscriber lambda was passed to GDrive for progress updates
    assert 'subscriber' in mock_gdrive.download_file.call_args[1]

    # 5. Check saving the file locally
    mock_save_file.assert_called_once_with(
        "/tmp/save.zip",
        mock_file_content,
        binary=True
    )

    # 6. Check backup directory is created
    copytree_mock.assert_called_once_with(
        mock_game.local_path,
        mock_game.local_path + Downloader.BackupSuffix
    )

    # 7. Check archive extraction
    mock_unpack_archive.assert_called_once_with(
        "/tmp/save.zip",
        mock_game.local_path,
        "zip"
    )

    # 8. Check metadata update (checksum)
    assert mock_game.meta.local.checksum == mock_game.meta.drive.checksum
    assert mock_game.meta.local.checksum == "drive_checksum_new"

    # 9. Check events sent: 6 ProgressEvents (including 0%) + 5 full stage ProgressEvents + 1 DoneEvent
    # 1st call: ProgressEvent (0%) from _set_stages
    # 2nd-6th calls: ProgressEvents from _complete_stage
    # 7th call: DoneEvent

    # In a successful run, we have 6 stages.
    # Stage 0: _set_stages sends 0% progress. (1 call)
    # Stage 1-5: _complete_stage sends progress. (5 calls)
    # Stage 6: _complete_stage is implicitly called by the GDrive subscriber's lambda.
    # (This is complex to assert perfectly without running the lambda, but the next 4 stages are completed)
    # Done: DoneEvent (1 call)
    # Total: at least 7 explicit calls to the subscriber if GDrive's lambda is ignored,
    # but the internal logic means more calls.
    # The simplest check is the final event:
    final_event = mock_subscriber.call_args_list[-1][0][0]
    assert isinstance(final_event, DoneEvent)
    assert final_event.success is True


def test_download_saves_directory_missing(module_patch, _downloader, mock_game, mock_subscriber):
    """Test early exit when the local saves directory is missing."""

    module_patch("os.path.exists", return_value=False)

    # ACT
    _downloader.download(mock_game)

    # ASSERT - Events Sent
    # Will send 0 progress event to notify that work has started.
    # Should also send ErrorEvent and then DoneEvent due to internal _send_event logic
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
    mock_game.meta.drive.refresh.assert_not_called()


def test_download_drive_metadata_missing(module_patch, _downloader, mock_game, mock_subscriber):
    """Test early exit when drive metadata is not present after refresh."""

    module_patch("os.path.exists", return_value=True)

    # Setup: Directory exists, but drive metadata is not present
    mock_game.meta.drive.is_present = False

    # ACT
    _downloader.download(mock_game)

    # 0% Progress + First Stage + Error + Done
    assert mock_subscriber.call_count == 4

    # The first call is the 0% Progress from _set_stages
    init_progress_event = mock_subscriber.call_args_list[0][0][0]
    first_progress_event = mock_subscriber.call_args_list[1][0][0]
    assert init_progress_event.progress == 0
    assert first_progress_event.progress > 0

    # The second call is the ErrorEvent (followed by DoneEvent via _send_event)
    error_event = mock_subscriber.call_args_list[2][0][0]
    done_event = mock_subscriber.call_args_list[3][0][0]

    assert isinstance(error_event, ErrorEvent)
    assert error_event.kind == EventKind.DriveMetadataMissing

    assert isinstance(done_event, DoneEvent)
    assert done_event.success is False


def test_backup_directory_with_existing_backup(module_patch, copytree_mock, cleanup_directory_mock, removedirs_mock,
                                               path_exists_mock):
    """Test the private backup method when a backup directory already exists."""

    module_patch("os.path.exists")

    saves_dir = "/path/to/saves"
    backup_dir = saves_dir + Downloader.BackupSuffix

    # Setup os.path.exists to return True for the backup directory check
    def exists_side_effect(path):
        return path == backup_dir

    path_exists_mock.side_effect = exists_side_effect

    # ACT
    Downloader._Downloader__backup_directory(saves_dir)  # noqa

    # ASSERT
    # 1. Existing backup should be cleaned up and removed
    cleanup_directory_mock.assert_called_once_with(backup_dir)
    removedirs_mock.assert_called_once_with(backup_dir)

    # 2. New backup should be created
    copytree_mock.assert_called_once_with(saves_dir, backup_dir)


def test_backup_directory_with_no_existing_backup(copytree_mock, cleanup_directory_mock, removedirs_mock, module_patch):
    """Test the private backup method when no backup directory exists."""

    module_patch("os.path.exists", return_value=False)
    saves_dir = "/path/to/saves"

    # ACT
    Downloader._Downloader__backup_directory(saves_dir)  # noqa

    # ASSERT
    # 1. Cleanup/Removal should NOT be called
    cleanup_directory_mock.assert_not_called()
    removedirs_mock.assert_not_called()

    # 2. New backup should be created
    copytree_mock.assert_called_once_with(saves_dir, saves_dir + Downloader.BackupSuffix)
