import pytest
from unittest.mock import MagicMock, call

from savegem.app.gui.constants import UIRefreshEvent
from savegem.gdrive_watcher.main import GDriveWatcher


@pytest.fixture(autouse=True)
def _setup(module_patch, resolve_temp_file_mock, path_exists_mock, games_config):
    # By default, assume GUI is initialized (flag file exists)
    resolve_temp_file_mock.return_value = "/mock/temp/gui_flag.txt"
    path_exists_mock.return_value = True
    games_config.current.drive_directory = "MOCKED_DRIVE_DIR_ID"

    def mock_daemon_init(self, service_name, requires_auth):
        self.__service_name = service_name
        self.__requires_auth = requires_auth
        self._Daemon__interval = 5.0  # Set private name-mangled attribute directly
        self._logger = MagicMock()

    module_patch("Daemon.__init__", side_effect=mock_daemon_init)


def create_mock_changes_response(changes_list, new_token="NEXT_PAGE_TOKEN"):
    return {
        "newStartPageToken": new_token,
        "changes": changes_list
    }


def test_work_returns_if_gui_not_initialized(path_exists_mock, app_context, gdrive_mock):
    """
    Test _work exits early if the GUI flag file does not exist.
    """

    watcher = GDriveWatcher()
    path_exists_mock.return_value = False

    watcher._work()

    # Assert that GDrive and app logic were not executed
    app_context.user.initialize.assert_not_called()
    gdrive_mock.get_changes.assert_not_called()


def test_work_initializes_and_downloads_before_checking_changes(gdrive_mock, app_context):
    """
    Test that app initialization and download are run regardless of changes.
    """

    watcher = GDriveWatcher()

    # Set get_changes to return empty list so the main logic runs fully
    gdrive_mock.get_changes.return_value = create_mock_changes_response([])

    watcher._work()

    # Assert initialization flow
    app_context.user.initialize.assert_called_once()
    app_context.games.download.assert_called_once()
    gdrive_mock.get_changes.assert_called_once()


def test_get_changes_updates_token_and_extracts_ids(gdrive_mock):
    """
    Test __get_changes correctly processes changes and updates start_page_token.
    """

    watcher = GDriveWatcher()

    # Arrange: Initial token is None
    assert watcher._GDriveWatcher__start_page_token is None  # noqa

    changes_response = create_mock_changes_response([
        {
            "file": {"id": "FILE_A", "parents": ["PARENT_1"]},
            "removed": False
        },
        {
            "file": {"id": "FILE_B", "parents": ["PARENT_2"]},
            "removed": False
        }
    ], new_token="NEW_TOKEN_123")

    gdrive_mock.get_changes.return_value = changes_response

    # Act
    modified_files, affected_directories = watcher._GDriveWatcher__get_changes()  # noqa

    # Assert initial token was used and then updated
    gdrive_mock.get_changes.assert_called_once_with(None)
    assert watcher._GDriveWatcher__start_page_token == "NEW_TOKEN_123"  # noqa

    # Assert data extraction
    assert modified_files == ["FILE_A", "FILE_B"]
    assert affected_directories == ["PARENT_1", "PARENT_2"]


def test_get_changes_handles_removed_files_hack(gdrive_mock, app_context):
    """
    Test that removed files are handled by assuming current game files were affected.
    """

    watcher = GDriveWatcher()
    app_dir = app_context.games.current.drive_directory

    changes_response = create_mock_changes_response([
        {
            "file": {"id": "FILE_X", "parents": ["PARENT_X"]},
            "removed": False
        },
        {
            "file": None,
            "removed": True
        }  # Removed files don't contain file info
    ], new_token="NEW_TOKEN_2")

    gdrive_mock.get_changes.return_value = changes_response

    # Act
    modified_files, affected_directories = watcher._GDriveWatcher__get_changes()  # noqa

    # Assert removed item triggers the hack
    assert modified_files == ["FILE_X"]
    assert affected_directories == ["PARENT_X", app_dir]  # app_dir added due to removed=True


def test_work_sends_refresh_for_all_relevant_changes(gdrive_mock, app_context, games_config, app_config,
                                                     ui_socket_mock):
    """
    Test that all three relevant change types trigger the correct refresh events.
    """

    watcher = GDriveWatcher()

    # Arrange: Mock get_changes to return ALL relevant IDs/Directories
    modified_files = [
        app_config.games_config_file_id,  # GameConfigChange
        app_config.activity_log_file_id,  # ActivityLogUpdate
        "some_other_file_id"  # (Ignored)
    ]
    affected_directories = [
        games_config.current.drive_directory,  # CloudSaveFilesChange
        "some_other_dir_id"  # (Ignored)
    ]

    gdrive_mock.get_changes.return_value = create_mock_changes_response([], new_token="T1")
    # Manually inject the results __get_changes would return
    watcher._GDriveWatcher__get_changes = MagicMock(return_value=(modified_files, affected_directories))

    # Act
    watcher._work()

    # Assert that all three refresh commands were sent
    expected_calls = [
        call(UIRefreshEvent.CloudSaveFilesChange),
        call(UIRefreshEvent.GameConfigChange),
        call(UIRefreshEvent.ActivityLogUpdate),
    ]
    ui_socket_mock.send_ui_refresh_command.assert_has_calls(expected_calls, any_order=True)
    assert ui_socket_mock.send_ui_refresh_command.call_count == 3


def test_work_sends_no_refresh_if_no_relevant_changes(ui_socket_mock, app_context, gdrive_mock):
    """
    Test no refresh commands are sent if unrelated changes occur.
    """

    watcher = GDriveWatcher()

    # Arrange: Mock get_changes to return only unrelated IDs/Directories
    modified_files = ["unrelated_file_1", "unrelated_file_2"]
    affected_directories = ["unrelated_dir_1"]

    gdrive_mock.get_changes.return_value = create_mock_changes_response([], new_token="T2")
    watcher._GDriveWatcher__get_changes = MagicMock(return_value=(modified_files, affected_directories))

    # Act
    watcher._work()

    # Assert no refresh commands were sent
    ui_socket_mock.send_ui_refresh_command.assert_not_called()
