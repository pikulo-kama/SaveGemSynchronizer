import pytest
from PyQt6.QtCore import Qt
from pytest_mock import MockerFixture

from savegem.app.gui.thread import execute_in_blocking_thread


@pytest.fixture(autouse=True)
def _setup_dependencies(gui_mock, qtbot):  # noqa
    gui_mock.is_blocked = False


@pytest.fixture
def mock_worker(mocker: MockerFixture):
    """Provides a mock QWorker object."""
    worker = mocker.MagicMock()

    return worker


def test_execute_in_blocking_thread_blocks_gui(gui_mock, qthread_mock, mock_worker):
    """
    Test that the function correctly sets the wait cursor and blocks the GUI.
    """

    execute_in_blocking_thread(qthread_mock, mock_worker)

    # 1. Check GUI state change
    assert gui_mock.is_blocked is True

    # 2. Check cursor change
    gui_mock.setCursor.assert_called_with(Qt.CursorShape.WaitCursor)

    # 3. Check thread and worker initialization
    mock_worker.moveToThread.assert_called_with(qthread_mock)
    qthread_mock.start.assert_called_once()

    # 4. Check initial connections (we can't easily check the final 'on_finish' connection yet)
    qthread_mock.started.connect.assert_called_once_with(mock_worker.start)


def test_execute_in_blocking_thread_unblocks_on_finish(gui_mock, qthread_mock, mock_worker):
    """
    Test that the GUI unblocks and cursor is reset when the thread finishes.
    """
    # Set up a spy on the final finish callback
    execute_in_blocking_thread(qthread_mock, mock_worker)
    qthread_mock.finished.emit()

    # Verify the initial blocking state
    assert gui_mock.is_blocked is True

    # Simulate the thread finishing: Call the final connected handler directly.
    # The 'on_finish' function is the LAST thing connected to thread.finished.
    # We call the *fourth* connection made to thread.finished.connect
    # (quit, worker.deleteLater, thread.deleteLater, on_finish)

    # In a real test, we would look up the connected function. Since we're mocking,
    # we simulate the effect of the 'on_finish' function:

    gui_mock.setCursor.reset_mock()  # Reset mock to check the final state change

    on_finish_handler = qthread_mock.finished.connect.call_args_list[2][0][0]
    on_finish_handler()

    gui_mock.setCursor.assert_called_with(Qt.CursorShape.ArrowCursor)
    assert gui_mock.is_blocked is False


def test_execute_in_blocking_thread_avoids_redundant_execution(gui_mock, qthread_mock, mock_worker):
    """
    Test that the function returns immediately if the GUI is already blocked.
    """
    # Set GUI to blocked state before execution
    gui_mock.is_blocked = True

    execute_in_blocking_thread(qthread_mock, mock_worker)

    # 1. Check that the GUI state and cursor were not changed
    gui_mock.setCursor.assert_not_called()
    assert gui_mock.is_blocked is True  # State should remain True

    # 2. Check that the thread was not started and connections were not made
    qthread_mock.start.assert_not_called()
    mock_worker.moveToThread.assert_not_called()
    qthread_mock.started.connect.assert_not_called()

    # 3. Check the deleteLater/quit connections were skipped
    mock_worker.finished.connect.assert_not_called()
    assert qthread_mock.finished.connect.call_count == 0


def test_execute_in_blocking_thread_connects_cleanup(qthread_mock, mock_worker):
    """
    Test that all required signal connections for thread cleanup are made.
    """

    execute_in_blocking_thread(qthread_mock, mock_worker)

    # The worker.finished signal connects to thread.quit()
    mock_worker.finished.connect.assert_called_with(qthread_mock.quit)

    # thread.finished signal connects to:
    # 1. worker.deleteLater
    # 2. thread.deleteLater
    # 3. on_finish (The qthread_mock.finished.connect should be called 3 times total)
    assert qthread_mock.finished.connect.call_count == 3

    # Note: Checking the exact order and argument of the deleteLater calls is complex
    # with MagicMock. Asserting the call count provides good coverage for connection existence.
    qthread_mock.finished.connect.assert_any_call(mock_worker.deleteLater)
    qthread_mock.finished.connect.assert_any_call(qthread_mock.deleteLater)
