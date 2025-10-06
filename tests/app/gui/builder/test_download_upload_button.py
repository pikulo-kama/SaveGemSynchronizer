import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(app_context, games_config):
    games_config.current.local_path = "/path/to/save"


@pytest.fixture
def _download_worker_mock(module_patch):
    return module_patch("DownloadWorker")


@pytest.fixture
def _upload_worker_mock(module_patch):
    return module_patch("UploadWorker")


@pytest.fixture
def _buttons_builder(simple_gui):
    """
    Provides a fully mocked and initialized DownloadUploadButtonBuilder instance.
    """

    from savegem.app.gui.builder.download_upload_button import DownloadUploadButtonBuilder

    builder = DownloadUploadButtonBuilder()
    builder._gui = simple_gui

    return builder


def test_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor initializes the base class and internal attributes.
    """

    from savegem.app.gui.builder import UIBuilder
    from savegem.app.gui.builder.download_upload_button import DownloadUploadButtonBuilder
    from savegem.app.gui.constants import UIRefreshEvent

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)
    builder = DownloadUploadButtonBuilder()

    mock_super_init.assert_called_once_with(UIRefreshEvent.LanguageChange)
    assert builder._DownloadUploadButtonBuilder__download_button is None  # noqa
    assert builder._DownloadUploadButtonBuilder__upload_button is None  # noqa


def test_build_creates_buttons_and_sets_layout(mocker: MockerFixture, _buttons_builder, simple_gui):
    """
    Test build() creates buttons, sets properties, registers as interactable, and configures layout.
    """

    from savegem.app.gui.component.progress_button import QProgressPushButton
    from savegem.app.gui.constants import QAttr, QKind

    # Arrange: Spy on internal methods
    mock_add_interactable = mocker.patch.object(_buttons_builder, '_add_interactable')

    # Act
    _buttons_builder.build()

    upload_button = _buttons_builder._DownloadUploadButtonBuilder__upload_button  # noqa
    download_button = _buttons_builder._DownloadUploadButtonBuilder__download_button  # noqa

    # Assert 1: Buttons are created
    assert isinstance(upload_button, QProgressPushButton)
    assert isinstance(download_button, QProgressPushButton)

    # Assert 2: Properties are set
    assert upload_button.property(QAttr.Kind) == QKind.Primary
    assert upload_button.property(QAttr.Id) == "uploadButton"
    assert download_button.property(QAttr.Kind) == QKind.Secondary
    assert download_button.property(QAttr.Id) == "downloadButton"

    # Assert 3: Buttons are registered as interactable
    mock_add_interactable.assert_any_call(upload_button)
    mock_add_interactable.assert_any_call(download_button)

    # Assert 4: Button frame is added to the GUI layout
    simple_gui.center.layout().addWidget.assert_called_once()

    # Assert 5: Internal button layout configuration (using the frame argument)
    button_frame = simple_gui.center.layout().addWidget.call_args[0][0]
    button_layout = button_frame.layout()
    assert isinstance(button_layout, QHBoxLayout)
    assert button_layout.spacing() == 20
    assert button_layout.count() == 4  # Spacing, Upload, Download, Spacing

    # Check widgets added with correct stretch values
    # Item 1 (index 1) is upload_button, stretch=8
    assert button_layout.stretch(1) == 8
    # Item 2 (index 2) is download_button, stretch=2
    assert button_layout.stretch(2) == 2


def test_refresh_resets_progress_and_sets_text(mocker: MockerFixture, _buttons_builder, logger_mock, tr_mock):
    """
    Test refresh() resets progress, sets button text, and logs.
    """

    # Arrange: Initialize buttons via build()
    _buttons_builder.build()

    upload_button = _buttons_builder._DownloadUploadButtonBuilder__upload_button  # noqa

    # Spy on set_progress and setText to check calls
    mocker.patch.object(upload_button, 'set_progress')
    mocker.patch.object(upload_button, 'setText')
    mocker.patch.object(_buttons_builder._DownloadUploadButtonBuilder__download_button, 'set_progress')  # noqa

    # Act
    _buttons_builder.refresh()

    # Assert 1: Text Resource is called for the label
    tr_mock.assert_called_once_with("label_UploadSaveToDrive")

    # Assert 2: Progress is reset on both buttons
    upload_button.set_progress.assert_called_once_with(0)
    _buttons_builder._DownloadUploadButtonBuilder__download_button.set_progress.assert_called_once_with(0)  # noqa

    # Assert 3: Upload button text is set
    upload_button.setText.assert_called_once_with("Translated(label_UploadSaveToDrive)")

    # Assert 4: Logging is performed
    logger_mock.debug.assert_called_once()


def test_start_upload_initializes_and_runs_worker(mocker: MockerFixture, _buttons_builder, _upload_worker_mock):
    """
    Test __start_upload creates an UploadWorker and executes it.
    """

    _buttons_builder.build()
    mock_do_work = mocker.patch.object(_buttons_builder, '_do_work')

    upload_button = _buttons_builder._DownloadUploadButtonBuilder__upload_button  # noqa

    connect_error_spy = mocker.spy(_upload_worker_mock.return_value.error, "connect")
    connect_progress_spy = mocker.spy(_upload_worker_mock.return_value.progress, "connect")
    connect_completed_spy = mocker.spy(_upload_worker_mock.return_value.completed, "connect")

    _buttons_builder._DownloadUploadButtonBuilder__start_upload()  # noqa
    _upload_worker_mock.assert_called_once()

    mock_do_work.assert_called_once_with(_upload_worker_mock.return_value)

    assert connect_error_spy.call_count == 1
    assert connect_progress_spy.call_count == 1
    assert connect_completed_spy.call_count == 2  # __done_subscriber and self.refresh


def test_start_download_shows_confirmation(_buttons_builder, qtbot, confirmation_mock, tr_mock):
    """
    Test download button click calls confirmation popup with the correct text and callback.
    """

    # Arrange: Initialize buttons via build()
    _buttons_builder.build()
    download_button = _buttons_builder._DownloadUploadButtonBuilder__download_button  # noqa

    # Act: Simulate button click
    qtbot.mouseClick(download_button, Qt.MouseButton.LeftButton)

    # Assert 1: Confirmation popup is called
    confirmation_mock.assert_called_once()

    # Assert 2: Correct text resource is requested
    tr_mock.assert_called_once_with("confirmation_ConfirmToDownloadSave")

    # Assert 3: The callback passed to confirmation is the __start_download method
    # (Checking the second argument which is the callback function)
    assert confirmation_mock.call_args[0][
               1] == _buttons_builder._DownloadUploadButtonBuilder__start_download  # noqa


def test_start_download_initializes_and_runs_worker(mocker: MockerFixture, _buttons_builder, _download_worker_mock):
    """
    Test __start_download creates a DownloadWorker and executes it, connecting refresh/GUI update.
    """

    # Arrange: Initialize buttons via build()
    _buttons_builder.build()
    mock_do_work = mocker.patch.object(_buttons_builder, '_do_work')

    connect_error_spy = mocker.spy(_download_worker_mock.return_value.error, "connect")
    connect_progress_spy = mocker.spy(_download_worker_mock.return_value.progress, "connect")
    connect_completed_spy = mocker.spy(_download_worker_mock.return_value.completed, "connect")

    # Act
    _buttons_builder._DownloadUploadButtonBuilder__start_download()  # noqa

    # Assert 1: DownloadWorker is instantiated
    _download_worker_mock.assert_called_once()

    # Assert 2: Worker is passed to _do_work
    mock_do_work.assert_called_once_with(_download_worker_mock.return_value)

    # Assert 3: All necessary signals are connected (checking receivers)
    # error (1) + progress (1) + completed (__done, gui.refresh, self.refresh = 3) = 5
    assert connect_error_spy.call_count == 1
    assert connect_progress_spy.call_count == 1
    assert connect_completed_spy.call_count == 3


@pytest.mark.parametrize("success, expected_notification_call", [
    (True, True),
    (False, False),
])
def test_done_subscriber_notifies_on_success_only(notification_mock, success, expected_notification_call, tr_mock):
    """
    Test __done_subscriber calls notification only if the event is successful.
    """

    from savegem.common.service.subscriptable import DoneEvent, EventKind
    from savegem.app.gui.builder.download_upload_button import DownloadUploadButtonBuilder

    message_key = "test_message"
    callback = DownloadUploadButtonBuilder._DownloadUploadButtonBuilder__done_subscriber(message_key)  # noqa
    done_event = DoneEvent(None if success else EventKind.ErrorUploadingToDrive)

    # Act
    callback(done_event)

    # Assert
    if expected_notification_call:
        notification_mock.assert_called_once_with(f"Translated({message_key})")
    else:
        notification_mock.assert_not_called()


def test_progress_subscriber_sets_progress_on_widget(mocker: MockerFixture):
    """
    Test __progress_subscriber returns a callback that updates the widget's progress.
    """

    from savegem.app.gui.component.progress_button import QProgressPushButton
    from savegem.app.gui.builder.download_upload_button import DownloadUploadButtonBuilder

    # Arrange
    mock_button = mocker.MagicMock(spec=QProgressPushButton)
    callback = DownloadUploadButtonBuilder._DownloadUploadButtonBuilder__progress_subscriber(mock_button)  # noqa

    mock_event = mocker.MagicMock()
    mock_event.progress = 75

    # Act
    callback(mock_event)

    # Assert
    mock_button.set_progress.assert_called_once_with(75)


@pytest.mark.parametrize("event_kind, expected_tr_key", [
    ("SavesDirectoryMissing", "notification_ErrorSaveDirectoryMissing"),
    ("DriveMetadataMissing", "label_StorageIsEmpty"),
    ("ErrorUploadingToDrive", "notification_ErrorUploadingToDrive"),
    ("UnknownEvent", None),
])
def test_error_subscriber_notifies_on_specific_errors(notification_mock, tr_mock, games_config, event_kind,
                                                      expected_tr_key):
    """
    Test __error_subscriber handles specific error kinds and notifies the user.
    """

    from savegem.common.service.subscriptable import EventKind, ErrorEvent
    from savegem.app.gui.builder.download_upload_button import DownloadUploadButtonBuilder

    kind = None

    if event_kind == "SavesDirectoryMissing":
        kind = EventKind.SavesDirectoryMissing

    if event_kind == "DriveMetadataMissing":
        kind = EventKind.DriveMetadataMissing

    if event_kind == "ErrorUploadingToDrive":
        kind = EventKind.ErrorUploadingToDrive

    # Arrange
    error_event = ErrorEvent(kind)

    # Act
    DownloadUploadButtonBuilder._DownloadUploadButtonBuilder__error_subscriber(error_event)  # noqa

    # Assert
    if expected_tr_key:
        notification_mock.assert_called_once()
        # Check if 'tr' was called with the correct key
        assert expected_tr_key in tr_mock.call_args[0]

        # Check the specific case where the local path is included
        if event_kind == EventKind.SavesDirectoryMissing:
            assert games_config.current.local_path in tr_mock.call_args[0]

    else:
        notification_mock.assert_not_called()
