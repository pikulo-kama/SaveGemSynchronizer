from dataclasses import dataclass
from typing import Callable
from unittest.mock import MagicMock, PropertyMock

import pytest


@dataclass
class MockGameMeta:
    """
    Mocks the metadata structure required by ProcessWatcher.
    """

    local: MagicMock
    drive: MagicMock
    sync_status: any


@pytest.fixture
def _create_game_process():
    """
    Factory to create a mock GameProcess instance with controlled attributes.
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.game_process import GameProcess, ProcessStatus
    from tests.tools.mocks.mock_game import MockGame

    def _factory(name: str, has_started: bool = False, has_closed: bool = False,
                 auto_mode: bool = True, sync_status: SyncStatus = SyncStatus.UpToDate) -> GameProcess:

        # Create the full hierarchy
        metadata = MockGameMeta(
            local=MagicMock(),
            drive=MagicMock(),
            sync_status=sync_status
        )

        game = MockGame(
            name=name,
            process_name="",
            auto_mode_allowed=auto_mode,
            metadata=metadata
        )

        status = ProcessStatus.Running

        if has_started:
            status = ProcessStatus.Started

        elif has_closed:
            status = ProcessStatus.Closed

        return GameProcess(game, status)

    return _factory


@pytest.fixture
def _get_run_processes_mock(module_patch, _create_game_process: Callable) -> MagicMock:
    """
    Mocks the core function that returns active game processes.
    """
    return module_patch('get_running_game_processes')


def test_work_initial_dependencies(app_context, gdrive_mock, _get_run_processes_mock):
    """
    Test that required initialization steps are called before process checking.
    """

    from savegem.process_watcher.main import ProcessWatcher

    _get_run_processes_mock.return_value = []

    watcher = ProcessWatcher()
    watcher._work()

    # 1. Initialize user with GDrive info
    app_context.user.initialize.assert_called_once_with(
        gdrive_mock.get_current_user
    )
    # 2. Download games configuration
    app_context.games.download.assert_called_once()
    # 3. Get active processes
    _get_run_processes_mock.assert_called_once()


def test_work_returns_early_if_no_state_change(app_context, downloader_mock, _get_run_processes_mock,
                                               _create_game_process):
    """
    Test that _work returns immediately if no process has started or closed.
    """

    from savegem.process_watcher.main import ProcessWatcher

    # Create processes that are just 'Running'
    running_procs = [
        _create_game_process("Game A", has_started=False, has_closed=False),
        _create_game_process("Game B", has_started=False, has_closed=False),
    ]
    _get_run_processes_mock.return_value = running_procs

    watcher = ProcessWatcher()
    watcher._work()

    # Activity update and state check should NOT be called
    app_context.activity.update.assert_not_called()
    assert app_context.state.is_auto_mode.called is False

    # Downloader/Uploader should not be called
    downloader_mock.download.assert_not_called()


def test_work_updates_activity_log_for_running_games(app_context, _get_run_processes_mock, _create_game_process):
    """
    Test that the activity log is updated with currently running (non-closed) games.
    """

    from savegem.process_watcher.main import ProcessWatcher

    proc_started = _create_game_process("Started Game", has_started=True)
    proc_closed = _create_game_process("Closed Game", has_closed=True)
    proc_running = _create_game_process("Running Game", has_started=False, has_closed=False)

    _get_run_processes_mock.return_value = [proc_started, proc_closed, proc_running]

    # Set auto mode to False to ensure we don't accidentally call __perform_automatic_actions
    type(app_context.state).is_auto_mode = PropertyMock(return_value=False)

    watcher = ProcessWatcher()
    watcher._work()

    # Activity should only include Started Game and Running Game (i.e., not the closed one)
    app_context.activity.update.assert_called_once_with(
        ["Started Game", "Running Game"]
    )


def test_work_skips_auto_actions_when_disabled(app_context, downloader_mock, _get_run_processes_mock,
                                               _create_game_process):
    """
    Test that automatic actions are skipped if app.state.is_auto_mode is False.
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    proc_started = _create_game_process("Started Game", has_started=True, sync_status=SyncStatus.NoInformation)
    _get_run_processes_mock.return_value = [proc_started]

    # Mock auto mode to be False
    type(app_context.state).is_auto_mode = PropertyMock(return_value=False)

    watcher = ProcessWatcher()
    watcher._work()

    # The activity update is called (since a game started)
    app_context.activity.update.assert_called_once()

    # BUT, no download/upload should occur
    proc_started.game.meta.drive.refresh.assert_not_called()
    downloader_mock.mock_downloader.download.assert_not_called()


def test_auto_action_skip_if_game_auto_mode_disabled(app_context, downloader_mock, _get_run_processes_mock,
                                                     _create_game_process):
    """
    Test that automatic actions are skipped if game.auto_mode_allowed is False.
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    proc_started = _create_game_process(
        "Manual Game",
        has_started=True,
        auto_mode=False,
        sync_status=SyncStatus.NoInformation
    )
    _get_run_processes_mock.return_value = [proc_started]

    # Mock auto mode to be True
    type(app_context.state).is_auto_mode = PropertyMock(return_value=True)

    watcher = ProcessWatcher()
    watcher._work()

    # No refresh or download/upload
    proc_started.game.meta.drive.refresh.assert_not_called()
    downloader_mock.download.assert_not_called()


def test_auto_action_skip_if_uptodate(app_context, downloader_mock, _get_run_processes_mock, _create_game_process):
    """
    Test that automatic actions are skipped if sync_status is UpToDate, even if the game started.
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    proc_started = _create_game_process(
        "UpToDate Game",
        has_started=True,
        sync_status=SyncStatus.UpToDate
    )
    _get_run_processes_mock.return_value = [proc_started]

    # Mock auto mode to be True
    type(app_context.state).is_auto_mode = PropertyMock(return_value=True)

    watcher = ProcessWatcher()
    watcher._work()

    # Metadata refresh MUST be called to get the status
    proc_started.game.meta.drive.refresh.assert_called_once()

    # BUT, no download/upload should occur
    downloader_mock.download.assert_not_called()


def test_auto_skip_if_running(app_context, downloader_mock, push_notification_mock, _get_run_processes_mock,
                              _create_game_process):
    """
    Test that automatic actions skip processes that are running but have not just started or closed.
    This covers the 'if not process.has_started and not process.has_closed: continue' condition.
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    proc_started = _create_game_process("Started Game", has_started=True, sync_status=SyncStatus.NoInformation)

    # 2. Target process: Running, but neither started nor closed (should be skipped by 'continue')
    proc_running_target = _create_game_process("Running Target", has_started=False, has_closed=False)

    _get_run_processes_mock.return_value = [proc_started, proc_running_target]

    # Mock app auto mode to be True
    type(app_context.state).is_auto_mode = PropertyMock(return_value=True)

    watcher = ProcessWatcher()
    watcher._work()

    # The started process MUST proceed with refresh/download
    proc_started.game.meta.drive.refresh.assert_called_once()
    downloader_mock.return_value.download.assert_called_once()

    # The running process MUST be skipped before refresh
    proc_running_target.game.meta.drive.refresh.assert_not_called()


def test_auto_action_download_on_started(app_context, downloader_mock, push_notification_mock, ui_socket_mock,
                                         _get_run_processes_mock, _create_game_process, tr_mock):
    """
    Test full download workflow when a game starts and the save is modified (needs download).
    """

    from savegem.app.gui.constants import UIRefreshEvent
    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    game_name = "Started Game"
    proc_started = _create_game_process(
        game_name,
        has_started=True,
        sync_status=SyncStatus.NoInformation
    )
    _get_run_processes_mock.return_value = [proc_started]
    type(app_context.state).is_auto_mode = PropertyMock(return_value=True)

    watcher = ProcessWatcher()
    watcher._work()

    proc_started.game.meta.drive.refresh.assert_called_once()

    downloader_mock.return_value.download.assert_called_once_with(proc_started.game)

    push_notification_mock.assert_called_once_with("Translated(notification_NewSaveHasBeenDownloaded)")
    ui_socket_mock.send_ui_refresh_command.assert_called_once_with(
        UIRefreshEvent.CloudSaveFilesChange
    )


def test_auto_action_upload_on_closed(app_context, uploader_mock, push_notification_mock, ui_socket_mock,
                                      _get_run_processes_mock, _create_game_process, tr_mock):
    """
    Test full upload workflow when a game closes and the save is modified (needs upload).
    """

    from savegem.common.core.save_meta import SyncStatus
    from savegem.process_watcher.main import ProcessWatcher

    game_name = "Closed Game"
    proc_closed = _create_game_process(
        game_name,
        has_closed=True,
        sync_status=SyncStatus.NoInformation
    )
    _get_run_processes_mock.return_value = [proc_closed]
    type(app_context.state).is_auto_mode = PropertyMock(return_value=True)

    watcher = ProcessWatcher()
    watcher._work()

    proc_closed.game.meta.drive.refresh.assert_called_once()
    uploader_mock.return_value.upload.assert_called_once_with(proc_closed.game)
    push_notification_mock.assert_called_once_with("Translated(notification_SaveHasBeenUploaded)")
    ui_socket_mock.send_ui_refresh_command.assert_not_called()
