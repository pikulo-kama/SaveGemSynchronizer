from datetime import date

import pytest
import pytz
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QGridLayout
from pytest_mock import MockerFixture

from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.builder.save_status import SaveStatusBuilder
from savegem.app.gui.constants import UIRefreshEvent
from savegem.common.core.save_meta import SyncStatus


@pytest.fixture(autouse=True)
def _setup_dependencies(module_patch, tr_mock, app_context, games_config, app_state_mock, date_mock):

    tr_mock.side_effect = lambda key, *args: f"Translated({key}, {args})"

    games_config.current.meta.drive.is_present = False
    games_config.current.meta.drive.created_time = "2023-10-01T10:00:00.000Z"
    games_config.current.meta.drive.owner = "UserX"
    games_config.current.meta.sync_status = SyncStatus.UpToDate

    app_state_mock.locale = "en"
    date_mock.today.return_value = date(2024, 1, 15)  # Set a fixed "current" year
    module_patch("get_localzone", return_value=pytz.timezone("Europe/Kyiv"))
    module_patch("timezone", return_value=pytz.timezone("Europe/Kyiv"))
    module_patch("format_datetime", return_value=pytz.timezone("Europe/Kyiv"))


@pytest.fixture
def _status_builder(simple_gui):
    """
    Provides a fully mocked and initialized SaveStatusBuilder instance.
    """

    builder = SaveStatusBuilder()
    builder._gui = simple_gui

    return builder


def test_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor initializes the base class with all required refresh events.
    """

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)
    builder = SaveStatusBuilder()

    mock_super_init.assert_called_once_with(
        UIRefreshEvent.LanguageChange,
        UIRefreshEvent.GameConfigChange,
        UIRefreshEvent.CloudSaveFilesChange,
        UIRefreshEvent.GameSelectionChange,
        UIRefreshEvent.SaveDownloaded
    )

    assert builder._SaveStatusBuilder__save_status is None  # noqa
    assert builder._SaveStatusBuilder__last_save_timestamp is None  # noqa


def test_build_creates_labels_and_sets_layout(_status_builder, simple_gui):
    """
    Test build() creates labels, sets object names/alignment, and configures layouts.
    """

    # Act
    _status_builder.build()

    status_label = _status_builder._SaveStatusBuilder__save_status  # noqa
    timestamp_label = _status_builder._SaveStatusBuilder__last_save_timestamp  # noqa

    # Assert 1: Labels are created and internal attributes set
    assert isinstance(status_label, QLabel)
    assert isinstance(timestamp_label, QLabel)

    # Assert 2: Object names and alignment are set
    assert status_label.objectName() == "saveStatusLabel"
    assert timestamp_label.objectName() == "saveStatusTimestamp"
    assert status_label.alignment() == Qt.AlignmentFlag.AlignCenter

    # Assert 3: Info frame is added to the GUI center layout
    simple_gui.center.layout().addWidget.assert_called_once()

    # Assert 4: Internal QGridLayout setup
    info_frame = simple_gui.center.layout().addWidget.call_args[0][0]
    internal_layout = info_frame.layout()
    assert isinstance(internal_layout, QGridLayout)
    assert internal_layout.spacing() == 5

    # Assert 5: Labels are added to the grid (by row/column/alignment)
    # Check status label
    assert internal_layout.itemAtPosition(0, 0).widget() == status_label
    # Check timestamp label
    assert internal_layout.itemAtPosition(1, 0).widget() == timestamp_label


@pytest.mark.parametrize("status, expected_tr_key", [
    (SyncStatus.LocalOnly, "label_StorageIsEmpty"),
    (SyncStatus.NeedsDownload, "info_SaveNeedsToBeDownloaded"),
    (SyncStatus.UpToDate, "info_SaveIsUpToDate"),
])
def test_get_local_version_text_maps_sync_status_to_tr_key(games_config, tr_mock, status, expected_tr_key):
    """
    Test the correct message key is retrieved based on app.games.current.meta.sync_status.
    """

    # Arrange
    games_config.current.meta.sync_status = status

    # Act
    result = SaveStatusBuilder._SaveStatusBuilder__get_last_download_version_text()  # noqa

    # Assert
    tr_mock.assert_called_once_with(expected_tr_key)
    assert result == f"Translated({expected_tr_key}, ())"  # Check the mocked 'tr' return format


def test_get_drive_timestamp_returns_empty_string_if_not_present(tr_mock, games_config):
    """
    Test an empty string is returned if no drive metadata is present.
    """

    # Arrange
    games_config.current.meta.drive.is_present = False

    # Act
    result = SaveStatusBuilder._SaveStatusBuilder__get_last_save_info_text()  # noqa

    # Assert
    assert result == ""
    tr_mock.assert_not_called()


@pytest.mark.parametrize("creation_year, current_year, expected_format", [
    (2024, 2024, "d MMMM"),  # Current year: exclude YYYY
    (2023, 2024, "d MMMM YYYY")  # Different year: include YYYY
])
def test_get_drive_timestamp_formats_date_correctly(mocker: MockerFixture, module_patch, games_config, date_mock,
                                                    datetime_mock, format_datetime_mock, tr_mock, creation_year,
                                                    current_year, expected_format):
    """
    Test the function formats the date, handling timezone and year comparison
    by controlling the mocked datetime objects.
    """

    games_config.current.meta.drive.is_present = True
    games_config.current.meta.drive.created_time = f"{creation_year}-10-01T10:00:00.000Z"
    date_mock.today.return_value = date(current_year, 1, 1)  # Set the comparison year
    format_datetime_mock.return_value = "01 October"

    # 2. Mock the final datetime object used for year comparison and formatting
    mock_final_datetime = mocker.MagicMock()
    mock_final_datetime.year = creation_year  # Controls the 'if' condition
    mock_final_datetime.strftime.return_value = "10:00"  # Controls the time for tr()

    mock_as_timezone = mocker.MagicMock()
    mock_as_timezone.astimezone.return_value = mock_final_datetime

    module_patch("pytz.utc.localize", return_value=mock_as_timezone)

    mock_naive_dt = mocker.MagicMock()
    datetime_mock.strptime.return_value = mock_naive_dt

    SaveStatusBuilder._SaveStatusBuilder__get_last_save_info_text()  # noqa

    format_datetime_mock.assert_called_once()
    assert format_datetime_mock.call_args[0][1] == expected_format

    tr_mock.assert_called_once()
    tr_args = tr_mock.call_args[0]
    assert tr_args[0] == "info_NewestSaveOnDriveInformation"
    # The first two positional arguments are the date and time strings (mocked)
    # The third positional argument (index 3) is the owner
    assert tr_args[3] == games_config.current.meta.drive.owner


def test_refresh_updates_both_labels_and_logs(mocker: MockerFixture, _status_builder, logger_mock):
    """
    Test refresh() calls the static helpers, sets label text, and logs the output.
    """

    # Arrange: Initialize labels via build()
    _status_builder.build()

    # Spy on the two static helper methods
    mock_get_status = mocker.patch.object(
        _status_builder,
        "_SaveStatusBuilder__get_last_download_version_text",
        return_value="Status Label"
    )

    mock_get_timestamp = mocker.patch.object(
        _status_builder,
        "_SaveStatusBuilder__get_last_save_info_text",
        return_value="Timestamp Label"
    )

    # Act
    _status_builder.refresh()

    # Assert 1: Helpers are called
    mock_get_status.assert_called_once()
    mock_get_timestamp.assert_called_once()

    # Assert 2: Labels are updated with the helper's return values
    assert _status_builder._SaveStatusBuilder__save_status.text() == "Status Label"  # noqa
    assert _status_builder._SaveStatusBuilder__last_save_timestamp.text() == "Timestamp Label"  # noqa

    # Assert 3: Logging for both labels is performed
    logger_mock.debug.assert_any_call("Save status label was reloaded. (%s)", "Status Label")
    logger_mock.debug.assert_any_call("Last save information label was reloaded. (%s)", "Timestamp Label")
