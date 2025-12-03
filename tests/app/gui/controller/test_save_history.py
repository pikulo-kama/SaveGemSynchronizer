from datetime import datetime
import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestSaveHistoryListController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture, module_patch, _save_data, _widget_mock, _label_mock, string_to_date_mock,
               _progress_button_mock, _spacer_mock, _v_layout_mock, _h_layout_mock, get_verbose_date_mock,
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
    def _save_data(self, games_config_mock, _save_a, _save_b, _widget_mock, _progress_button_mock, _h_layout_mock):
        save_list = [_save_a, _save_b]

        _widget_mock.side_effect = [
            _save_a.record_container,
            _save_a.details_container,
            _save_b.record_container,
            _save_b.details_container
        ]
        _h_layout_mock.side_effect = [
            _save_a.record_container.layout.return_value,
            _save_b.record_container.layout.return_value
        ]
        games_config_mock.current.meta.drive.__iter__.return_value = save_list
        _progress_button_mock.side_effect = [_save_a.button, _save_b.button]

        return save_list

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
    def _save_list(self, mocker: MockerFixture):
        """
        Mocks the QScrollableWidget for the save history list.
        """
        return mocker.MagicMock()

    @pytest.fixture
    def _controller(self, _widget_manager):
        """
        Provides the SaveHistoryListController instance.
        """

        from savegem.app.gui.controller.save_history import SaveHistoryListController
        return SaveHistoryListController(_widget_manager)

    def test_refresh_renders_history_items(self, _controller, _widget_manager, _save_list, _widget_mock,
                                           _progress_button_mock, _spacer_mock, _save_data):
        """
        Tests that refresh iterates over metadata, sets properties, and handles conditional rendering.
        """

        from savegem.app.gui.constants import QBool

        add_widget_mock = _save_list.layout.return_value.add_dynamic_widget

        _controller.refresh(_save_list)

        _widget_manager.remove_child_widgets.assert_called_once_with(_save_list)
        add_widget_mock.assert_any_call(_spacer_mock.return_value)

        assert _widget_mock.call_count == 4  # Two records created. (once widget for record and another for details)
        assert _progress_button_mock.call_count == 2  # Two buttons created (one hidden later)
        assert add_widget_mock.call_count == 3

        for save in _save_data:
            save.record_container.setProperty.assert_called_once_with("active", QBool(save.is_current))
            record_container_layout = save.record_container.layout.return_value
            add_widget_args = record_container_layout.add_dynamic_widget.call_args_list
            add_widget_args = [arg[0][0] for arg in add_widget_args]

            if save.is_current:
               assert save.button not in add_widget_args
            else:
                assert save.button in add_widget_args

    def test_get_upload_date_string(self, _save_a):
        """
        Tests static method __get_upload_date_string returns correct formatted string.
        """

        from savegem.app.gui.controller.save_history import SaveHistoryListController

        # Note: Accessing private static method via name mangling
        result = SaveHistoryListController._SaveHistoryListController__get_upload_date_string(_save_a)  # noqa
        assert result == "Jan 1st, 2025 10:00 AM"

    def test_get_owner_string_found(self, _save_a):
        """
        Tests static method __get_owner_string returns owner name if user is found.
        """

        from savegem.app.gui.controller.save_history import SaveHistoryListController

        _save_a.email = "amy@a.com"

        result = SaveHistoryListController._SaveHistoryListController__get_owner_string(_save_a)  # noqa
        assert result == "Amy Adams"

    def test_get_owner_string_not_found_fallback(self, user_config_mock, _save_b):
        """
        Tests static method __get_owner_string returns email if user is not found.
        """

        from savegem.app.gui.controller.save_history import SaveHistoryListController

        _save_b.owner = "test"
        user_config_mock.by_email.return_value = None

        result = SaveHistoryListController._SaveHistoryListController__get_owner_string(_save_b)  # noqa
        # Should fall back to the email address
        assert result == "test"

    def test_restore_version_worker_flow(self, mocker: MockerFixture, module_patch, _controller, gui_mock,
                                         games_config_mock, _do_work_mock):
        """
        Tests the __restore_version logic, verifying worker setup and completion callback.
        """

        from savegem.common.service.subscriptable import DoneEvent, EventKind
        from savegem.app.gui.constants import UIRefreshEvent

        file_id = "v1-restore-id"
        mock_button = mocker.MagicMock()
        download_worker = module_patch("DownloadWorker")

        # Get the inner restore function
        restore_func = lambda: _controller._SaveHistoryListController__restore_version(file_id, mock_button)  # noqa
        restore_func()

        # 1. Assert worker setup
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
        gui_mock.refresh.assert_called_once_with(UIRefreshEvent.SaveDownloaded)
        gui_mock.notification.assert_called_once_with("Translated(notification_NewSaveHasBeenDownloaded)")

        # 5. Simulate FAILURE event (should do nothing)
        games_config_mock.current.meta.drive.refresh.reset_mock()
        gui_mock.refresh.reset_mock()
        gui_mock.notification.reset_mock()

        on_completed_callback(DoneEvent(EventKind.ErrorUploadingToDrive))

        assert games_config_mock.current.meta.drive.refresh.call_count == 0
