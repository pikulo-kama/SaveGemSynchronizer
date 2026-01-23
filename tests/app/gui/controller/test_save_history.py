from datetime import datetime
import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestSaveHistoryListController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture, module_patch, string_to_date_mock, get_verbose_date_mock,
               get_verbose_time_mock, tr_mock, games_config_mock, user_config_mock):

        games_config_mock.current.meta.local.checksum = "C2"

        string_to_date_mock.return_value = datetime(2025, 1, 1)
        get_verbose_date_mock.return_value = "Jan 1st, 2025"
        get_verbose_time_mock.return_value = "10:00 AM"

        def owner_by_email(email):
            owner = mocker.MagicMock()

            if email == "amy@a.com":
                owner.name = "Amy Adams"

            elif email == "bob@b.com":
                owner.name = "Bob Brody"
            else:
                return None

            return owner

        user_config_mock.by_email.side_effect = owner_by_email

    @pytest.fixture
    def _save_a(self, mocker: MockerFixture):
        save = mocker.MagicMock()
        save.id = "v1_id"
        save.checksum = "C1"
        save.created_time = "2025-01-01"
        save.owner = "amy@a.com"
        save.is_current = False

        return save

    @pytest.fixture
    def _save_b(self, mocker: MockerFixture):
        save = mocker.MagicMock()
        save.id = "v2_id"
        save.checksum = "C2"
        save.created_time = "2025-01-02"
        save.owner = "bob@b.com"
        save.is_current = True

        return save

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the SaveHistoryListController instance.
        """

        from src.savegem import SaveHistoryListController
        return SaveHistoryListController(_widget_manager)

    def test_get_data(self, _controller, games_config_mock):
        assert _controller._get_data() == games_config_mock.current.meta.drive

    def test_resolve(self, mocker: MockerFixture, _controller):

        metadata = mocker.MagicMock()
        expected_version = "1.0.0"
        expected_owner = "Arnold"

        version_mock = mocker.patch.object(_controller, "_SaveHistoryListController__get_upload_date_string")
        owner_mock = mocker.patch.object(_controller, "_SaveHistoryListController__get_owner_string")

        version_mock.return_value = expected_version
        owner_mock.return_value = expected_owner

        version_result = _controller.resolve(metadata, "version")
        owner_result = _controller.resolve(metadata, "owner")
        invalid_result = _controller.resolve(metadata, "test")

        assert version_result == expected_version
        assert owner_result == expected_owner
        assert invalid_result is None

    def test_handle_history_record(self, mocker: MockerFixture, _controller, _save_a, games_config_mock):

        from src.savegem import SaveHistoryListController
        from src.savegem import QBool

        history_record = mocker.MagicMock()

        # Test when history record metadata doesn't match local save metadata.
        games_config_mock.current.meta.local.checksum = None

        _controller.handle__history_record(history_record, _save_a)

        history_record.setProperty.assert_called_once_with(SaveHistoryListController.HistoryRecordActive, QBool(False))

        # Test when history record metadata does match local save metadata.
        history_record.reset_mock()
        games_config_mock.current.meta.local.checksum = _save_a.checksum

        _controller.handle__history_record(history_record, _save_a)

        history_record.setProperty.assert_called_once_with(SaveHistoryListController.HistoryRecordActive, QBool(True))

    def test_handle_restore_button(self, mocker: MockerFixture, _controller, _save_a, games_config_mock,
                                   _widget_manager, gui_mock, tr_mock):

        button = mocker.MagicMock()
        button.metadata.name = "Upload Button"

        spacer = mocker.MagicMock()
        spacer.metadata.name = "Spacer"

        # Verify that restore button is not being removed
        # If save file checksum doesn't match local save checksum.
        games_config_mock.current.meta.local.checksum = None

        _controller.handle__restore_button(button, _save_a)

        _widget_manager.delete.assert_not_called()

        # Verify that restore button is removed when
        # checksum matches.
        games_config_mock.current.meta.local.checksum = _save_a.checksum
        button.reset_mock()

        _controller.handle__restore_button(button, _save_a)

        _widget_manager.delete.assert_called_once()
        delete_filter = _widget_manager.delete.call_args[0][0]
        assert delete_filter(button.metadata) is True
        assert delete_filter(spacer.metadata) is False

        # Verify restore version callback.
        restore_version_mock = mocker.patch.object(_controller, "_SaveHistoryListController__restore_version")

        button.clicked.connect.assert_called_once()
        restore_version_local = button.clicked.connect.call_args[0][0]
        confirmation_callback = restore_version_local()
        confirmation_callback()

        gui_mock.confirmation.assert_called_once()
        tr_mock.assert_called_once_with("confirmation_ConfirmToDownloadSave")
        restore_version_callback = gui_mock.confirmation.call_args[0][1]
        restore_version_callback()

        restore_version_mock.assert_called_once_with(_save_a.id, button)

    def test_get_upload_date_string(self, _save_a):
        """
        Tests static method __get_upload_date_string returns correct formatted string.
        """

        from src.savegem import SaveHistoryListController

        # Note: Accessing private static method via name mangling
        result = SaveHistoryListController._SaveHistoryListController__get_upload_date_string(_save_a)  # noqa
        assert result == "Jan 1st, 2025 10:00 AM"

    def test_get_owner_string_found(self, _save_a):
        """
        Tests static method __get_owner_string returns owner name if user is found.
        """

        from src.savegem import SaveHistoryListController

        _save_a.email = "amy@a.com"

        result = SaveHistoryListController._SaveHistoryListController__get_owner_string(_save_a)  # noqa
        assert result == "Amy Adams"

    def test_get_owner_string_not_found_fallback(self, user_config_mock, _save_b):
        """
        Tests static method __get_owner_string returns email if user is not found.
        """

        from src.savegem import SaveHistoryListController

        _save_b.owner = "test"
        user_config_mock.by_email.return_value = None

        result = SaveHistoryListController._SaveHistoryListController__get_owner_string(_save_b)  # noqa
        # Should fall back to the email address
        assert result == "test"

    def test_restore_version_worker_flow(self, mocker: MockerFixture, module_patch, _controller, gui_mock,
                                         games_config_mock, _do_work_mock, _widget_manager):
        """
        Tests the __restore_version logic, verifying worker1 setup and completion callback.
        """

        from src.savegem.common.service.subscriptable import DoneEvent, EventKind
        from src.savegem import UIRefreshEvent

        file_id = "v1-restore-id"
        mock_button = mocker.MagicMock()
        download_worker = module_patch("DownloadWorker")

        # Get the inner restore function
        restore_func = lambda: _controller._SaveHistoryListController__restore_version(file_id, mock_button)  # noqa
        restore_func()

        # 1. Assert worker1 setup
        download_worker.assert_called_once_with(file_id)
        _do_work_mock.assert_called_once_with(download_worker.return_value)

        # 2. Assert progress connection
        download_worker.return_value.progress.connect.assert_called_once()

        # 3. Get the on_completed callback
        on_completed_callback = download_worker.return_value.completed.connect.call_args[0][0]

        # 4. Simulate SUCCESS event
        on_completed_callback(DoneEvent(None))

        # Assert post-success actions
        games_config_mock.current.meta.drive.refresh.assert_called_once()
        _widget_manager.event_refresh.assert_called_once_with(UIRefreshEvent.SaveDownloaded)
        gui_mock.notification.assert_called_once_with("Translated(notification_NewSaveHasBeenDownloaded)")

        # 5. Simulate FAILURE event (should do nothing)
        games_config_mock.current.meta.drive.refresh.reset_mock()
        gui_mock.refresh.reset_mock()
        gui_mock.notification.reset_mock()

        on_completed_callback(DoneEvent(EventKind.ErrorUploadingToDrive))

        assert games_config_mock.current.meta.drive.refresh.call_count == 0
