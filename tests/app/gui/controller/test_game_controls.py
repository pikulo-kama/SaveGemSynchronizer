import pytest
from unittest.mock import ANY
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


class TestSubscribers:

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    def test_done_subscriber_success_notifies(self, gui_mock):
        """
        Test notification is sent when DoneEvent.success is True.
        """

        from savegem.app.gui.controller.game_controls import _done_subscriber
        from savegem.common.service.subscriptable import DoneEvent

        callback = _done_subscriber("notification_Message")
        callback(DoneEvent(None))

        gui_mock.notification.assert_called_once_with("Translated(notification_Message)")

    def test_done_subscriber_failure_does_not_notify(self, gui_mock):
        """
        Test no notification is sent when DoneEvent.success is False.
        """

        from savegem.app.gui.controller.game_controls import _done_subscriber
        from savegem.common.service.subscriptable import DoneEvent, EventKind

        callback = _done_subscriber("notification_Message")

        callback(DoneEvent(EventKind.ErrorUploadingToDrive))
        gui_mock.notification.assert_not_called()

    def test_progress_subscriber_sets_widget_progress(self, mocker: MockerFixture):
        """
        Test progress event updates the QProgressPushButton widget.
        """

        from savegem.app.gui.controller.game_controls import _progress_subscriber

        mock_widget = mocker.MagicMock()

        callback = _progress_subscriber(mock_widget)
        callback(mocker.MagicMock(progress=42))

        mock_widget.set_progress.assert_called_once_with(42)

    def test_error_subscriber_saves_directory_missing(self, gui_mock, games_config_mock):
        """
        Test notification for SavesDirectoryMissing error.
        """

        from savegem.common.service.subscriptable import EventKind, ErrorEvent
        from savegem.app.gui.controller.game_controls import _error_subscriber

        games_config_mock.current.local_path = "/mock/path/to/saves"

        event = ErrorEvent(EventKind.SavesDirectoryMissing)
        _error_subscriber(event)

        gui_mock.notification.assert_called_once_with(
            "Translated(notification_ErrorSaveDirectoryMissing, /mock/path/to/saves)"
        )

    def test_error_subscriber_drive_metadata_missing(self, gui_mock):
        """
        Test notification for DriveMetadataMissing error.
        """

        from savegem.common.service.subscriptable import EventKind, ErrorEvent
        from savegem.app.gui.controller.game_controls import _error_subscriber

        event = ErrorEvent(EventKind.DriveMetadataMissing)
        _error_subscriber(event)

        gui_mock.notification.assert_called_once_with("Translated(label_StorageIsEmptyDesc)")

    def test_error_subscriber_uploading_to_drive(self, gui_mock):
        """
        Test notification for DriveMetadataMissing error.
        """

        from savegem.common.service.subscriptable import EventKind, ErrorEvent
        from savegem.app.gui.controller.game_controls import _error_subscriber

        event = ErrorEvent(EventKind.ErrorUploadingToDrive)
        _error_subscriber(event)

        gui_mock.notification.assert_called_once_with("Translated(notification_ErrorUploadingToDrive)")


class TestDownloadButtonController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    @pytest.fixture(autouse=True)
    def _download_worker(self, module_patch):
        """
        Mocks the DownloadWorker class and returns the mock instance.
        """
        return module_patch("DownloadWorker").return_value

    @pytest.fixture
    def _mock_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    def test_setup_connects_to_confirmation_dialog(self, _widget_manager, _mock_button, gui_mock):
        """
        Tests that the button's clicked signal is connected to the gui().confirmation wrapper.
        """

        from savegem.app.gui.controller.game_controls import DownloadButtonController

        controller = DownloadButtonController(_widget_manager)
        controller.setup(_mock_button)

        _mock_button.clicked.connect.assert_called_once()
        outer_callback = _mock_button.clicked.connect.call_args[0][0]

        outer_callback()  # Simulate button click

        gui_mock.confirmation.assert_called_once_with(
            "Translated(confirmation_ConfirmToDownloadSave)",
            ANY  # The inner start_download function
        )

    def test_start_download_worker_connections(self, module_patch, _widget_manager, _mock_button, _download_worker,
                                               _do_work_mock, games_config_mock, gui_mock):
        """
        Tests the execution path inside the start_download function, verifying worker1 setup.
        """

        from savegem.app.gui.controller.game_controls import DownloadButtonController
        from savegem.app.gui.constants import UIRefreshEvent

        mock_error_sub = module_patch("_error_subscriber")
        mock_progress_sub = module_patch("_progress_subscriber")
        mock_done_sub = module_patch("_done_subscriber")

        controller = DownloadButtonController(_widget_manager)
        controller.setup(_mock_button)

        # Invoked callback attached to button.
        click_button = _mock_button.clicked.connect.call_args[0][0]
        click_button()

        # Get the inner 'start_download' function passed to gui.confirmation
        start_download = gui_mock.confirmation.call_args[0][1]
        start_download()  # Execute the download logic

        _do_work_mock.assert_called_once_with(_download_worker)
        assert _download_worker.completed.connect.call_count == 4

        _download_worker.error.connect.assert_called_once_with(mock_error_sub)
        mock_progress_sub.assert_called_once_with(_mock_button)
        mock_done_sub.assert_called_once_with("notification_NewSaveHasBeenDownloaded")

        for call in _download_worker.completed.connect.call_args_list:
            callback = call[0][0]
            callback()

        _mock_button.refresh.assert_called_once()
        _widget_manager.event_refresh.assert_called_once_with(UIRefreshEvent.SaveDownloaded)
        games_config_mock.current.meta.local.calculate_checksum.assert_called_once()


class TestUploadButtonController(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    @pytest.fixture
    def _upload_worker(self, module_patch):
        """
        Mocks the UploadWorker class and returns the mock instance.
        """
        return module_patch("UploadWorker").return_value

    @pytest.fixture
    def _mock_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    def test_setup_connects_to_start_upload(self, _widget_manager, _mock_button, gui_mock):
        """
        Tests that the button's clicked signal is connected directly to the start_upload wrapper.
        """

        from savegem.app.gui.controller.game_controls import UploadButtonController

        controller = UploadButtonController(_widget_manager)
        controller.setup(_mock_button)

        _mock_button.clicked.connect.assert_called_once()
        start_upload = _mock_button.clicked.connect.call_args[0][0]

        assert callable(start_upload)

    def test_start_upload_worker_connections(self, module_patch, _widget_manager, _mock_button, _upload_worker,
                                               _do_work_mock, games_config_mock, gui_mock):
        """
        Tests the execution path inside the start_upload function, verifying worker1 setup.
        """

        from savegem.app.gui.controller.game_controls import UploadButtonController

        mock_progress_sub = module_patch("_progress_subscriber")
        mock_done_sub = module_patch("_done_subscriber")

        controller = UploadButtonController(_widget_manager)
        controller.setup(_mock_button)

        start_upload = _mock_button.clicked.connect.call_args[0][0]
        start_upload()  # Execute the upload logic

        _do_work_mock.assert_called_once_with(_upload_worker)
        assert _upload_worker.completed.connect.call_count == 3

        mock_progress_sub.assert_called_once_with(_mock_button)
        mock_done_sub.assert_called_once_with("notification_SaveHasBeenUploaded")

        for call in _upload_worker.completed.connect.call_args_list:
            callback = call[0][0]
            callback()

        _mock_button.refresh.assert_called_once()
        games_config_mock.current.meta.drive.refresh.assert_called_once()
