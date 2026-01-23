import pytest

from pytest_mock import MockerFixture


class TestDownloader:

    @pytest.fixture
    def _mock_game(self, mocker: MockerFixture):
        """
        Fixture to create a mock Game object with necessary nested mocks
        """

        mock_game = mocker.Mock()
        drive_meta_mock = mocker.MagicMock()

        mock_game.local_path = "/path/to/local/saves"
        mock_game.meta.drive.is_present = True
        drive_meta_mock.id = "drive_file_id"
        drive_meta_mock.checksum = "drive_checksum_new"
        mock_game.meta.local.checksum = "local_checksum_old"

        mock_game.meta.drive.latest = drive_meta_mock

        # Ensure refresh is available
        mock_game.meta.drive.refresh = mocker.Mock()

        return mock_game


    @pytest.fixture
    def _mock_subscriber(self, mocker: MockerFixture):
        """
        Fixture for a mock subscriber function to check sent events.
        """
        return mocker.Mock()


    @pytest.fixture
    def _downloader(self, _mock_subscriber):
        """
        Fixture for the Downloader instance with a subscribed mock.
        """

        from src.savegem.common.service.downloader import Downloader

        downloader = Downloader()
        downloader.subscribe(_mock_subscriber)

        return downloader


    def test_download_success(self, path_exists_mock, copytree_mock, removedirs_mock, resolve_temp_file_mock,
                              save_file_mock, _downloader, cleanup_directory_mock, _mock_game, _mock_subscriber,
                              unpack_archive_mock, gdrive_mock):
        """
        Test a successful full download process.
        """

        from src.savegem.common.service.downloader import Downloader
        from src.savegem.common.service.subscriptable import DoneEvent

        resolve_temp_file_mock.return_value = "/tmp/save.zip"
        path_exists_mock.return_value = True  # Directory exists

        # Setup GDrive mock to return a BytesIO object (simulating file resolver)
        mock_file_content = b"save_data"
        gdrive_mock.download_file.return_value.getvalue.return_value = mock_file_content

        # ACT
        _downloader.download(_mock_game)

        # ASSERT - Execution Flow (6 stages + DoneEvent)

        # 1. Check game directory check (mocked as True)
        path_exists_mock.assert_any_call(_mock_game.local_path)

        # 2. Check stages set and initial 0% progress sent
        # (The Downloader is a SubscriptableService, which sends 0% progress on _set_stages)
        assert _mock_subscriber.call_count > 0

        # 3. Check metadata refresh
        _mock_game.meta.drive.refresh.assert_called_once()

        # 4. Check GDrive download and subscriber setup
        gdrive_mock.download_file.assert_called_once()
        # Check that a subscriber lambda was passed to GDrive for progress updates
        assert 'subscriber' in gdrive_mock.download_file.call_args[1]

        # 5. Check saving the file locally
        save_file_mock.assert_called_once_with(
            "/tmp/save.zip",
            mock_file_content,
            binary=True
        )

        # 6. Check backup directory is created
        copytree_mock.assert_called_once_with(
            _mock_game.local_path,
            _mock_game.local_path + Downloader.BackupSuffix
        )

        # 7. Check archive extraction
        unpack_archive_mock.assert_called_once_with(
            "/tmp/save.zip",
            _mock_game.local_path,
            "zip"
        )

        # 8. Check metadata update (checksum)
        assert _mock_game.meta.local.checksum == _mock_game.meta.drive.latest.checksum
        assert _mock_game.meta.local.checksum == "drive_checksum_new"

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
        final_event = _mock_subscriber.call_args_list[-1][0][0]
        assert isinstance(final_event, DoneEvent)
        assert final_event.success is True


    def test_download_saves_directory_missing(self, path_exists_mock, _downloader, _mock_game, _mock_subscriber):
        """
        Test early exit when the local saves directory is missing.
        """

        from src.savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind, ProgressEvent

        path_exists_mock.return_value = False

        # ACT
        _downloader.download(_mock_game)

        # ASSERT - Events Sent
        # Will send 0 progress event to notify that work has started.
        # Should also send ErrorEvent and then DoneEvent due to internal _send_event logic
        assert _mock_subscriber.call_count == 3

        progress_event = _mock_subscriber.call_args_list[0][0][0]
        error_event = _mock_subscriber.call_args_list[1][0][0]
        done_event = _mock_subscriber.call_args_list[2][0][0]

        assert isinstance(progress_event, ProgressEvent)
        assert progress_event.kind is None
        assert progress_event.progress == 0

        assert isinstance(error_event, ErrorEvent)
        assert error_event.kind == EventKind.SavesDirectoryMissing

        assert isinstance(done_event, DoneEvent)
        assert done_event.success is False
        assert done_event.kind == EventKind.SavesDirectoryMissing

        # ASSERT - Early Exit
        _mock_game.meta.drive.refresh.assert_not_called()


    def test_download_drive_metadata_missing(self, _downloader, _mock_game, _mock_subscriber, path_exists_mock):
        """
        Test early exit when drive metadata is not present after refresh.
        """

        from src.savegem.common.service.subscriptable import DoneEvent, ErrorEvent, EventKind

        path_exists_mock.return_value = True

        # Setup: Directory exists, but drive metadata is not present
        _mock_game.meta.drive.is_present = False

        # ACT
        _downloader.download(_mock_game)

        # 0% Progress + First Stage + Error + Done
        assert _mock_subscriber.call_count == 4

        # The first call is the 0% Progress from _set_stages
        init_progress_event = _mock_subscriber.call_args_list[0][0][0]
        first_progress_event = _mock_subscriber.call_args_list[1][0][0]
        assert init_progress_event.progress == 0
        assert first_progress_event.progress > 0

        # The second call is the ErrorEvent (followed by DoneEvent via _send_event)
        error_event = _mock_subscriber.call_args_list[2][0][0]
        done_event = _mock_subscriber.call_args_list[3][0][0]

        assert isinstance(error_event, ErrorEvent)
        assert error_event.kind == EventKind.DriveMetadataMissing

        assert isinstance(done_event, DoneEvent)
        assert done_event.success is False


    def test_backup_directory_with_existing_backup(self, copytree_mock, cleanup_directory_mock, removedirs_mock,
                                                   path_exists_mock):
        """
        Test the private backup method when a backup directory already exists.
        """

        from src.savegem.common.service.downloader import Downloader

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


    def test_backup_directory_with_no_existing_backup(self, copytree_mock, cleanup_directory_mock, removedirs_mock,
                                                      path_exists_mock):
        """
        Test the private backup method when no backup directory exists.
        """

        from src.savegem.common.service.downloader import Downloader

        path_exists_mock.return_value = False
        saves_dir = "/path/to/saves"

        # ACT
        Downloader._Downloader__backup_directory(saves_dir)  # noqa

        # ASSERT
        # 1. Cleanup/Removal should NOT be called
        cleanup_directory_mock.assert_not_called()
        removedirs_mock.assert_not_called()

        # 2. New backup should be created
        copytree_mock.assert_called_once_with(saves_dir, saves_dir + Downloader.BackupSuffix)

    def test_should_use_specific_save_file_id_to_download_if_provided(self, mocker: MockerFixture, _downloader,
                                                                      games_config_mock, _mock_game, path_exists_mock,
                                                                      gdrive_mock, save_file_mock, unpack_archive_mock,
                                                                      listdir_mock, removedirs_mock, copytree_mock):

        other_meta = mocker.MagicMock()
        other_meta.id = "test_id"
        other_meta.checksum = "OTHER_CHECKSUM"

        _mock_game.meta.drive.by_id.return_value = other_meta
        path_exists_mock.return_value = True

        _downloader.download(_mock_game, "test_id")

        assert _mock_game.meta.local.checksum == other_meta.checksum
        assert _mock_game.meta.local.checksum == "OTHER_CHECKSUM"
