import os
import sys
from unittest import mock

import psutil
import pytest

CURRENT_REAL_EXE = os.path.realpath(sys.executable)


def create_mock_process(name: str, pid: int = 123, exe_path: str = None) -> mock.Mock:
    """
    Creates a mock psutil.Process object with a configurable name() method.
    """

    mock_proc = mock.Mock(spec=psutil.Process)
    mock_proc.pid = pid
    mock_proc.name.return_value = name
    mock_proc.exe.return_value = str(exe_path)

    return mock_proc


@pytest.fixture
def _process_iter(module_patch):
    return module_patch("psutil.process_iter")


@pytest.fixture
def _system_env(module_patch):
    module_patch("os.getpid", return_value=100)  # noqa

    # Patch sys.executable to the expected real path
    module_patch("sys.executable", CURRENT_REAL_EXE)

    # Patch os.path.realpath to use the real function, but ensure the current
    # executable path is consistently the mock one.
    # We patch it globally and wrap the actual function.
    mock_realpath = mock.Mock(wraps=os.path.realpath)
    module_patch("os.path.realpath", new=mock_realpath)

    return mock_realpath


def test_all_processes_found(_process_iter):
    """
    Tests that all requested processes are returned, ignoring irrelevant ones.
    """

    from savegem.common.util.process import get_running_processes

    requested_names = ["chrome.exe", "spotify.exe"]

    # Create mock process objects that match the requested names
    mock_proc_1 = create_mock_process("chrome.exe", pid=100)
    mock_proc_2 = create_mock_process("spotify.exe", pid=200)

    # Configure the iterator to yield a mix of processes
    _process_iter.return_value = [
        create_mock_process("irrelevant.exe"),
        mock_proc_1,
        create_mock_process("another_irrelevant.exe"),
        mock_proc_2
    ]

    running = get_running_processes(requested_names)

    # Use standard pytest 'assert' for verification
    assert len(running) == 2
    found_names = sorted([p.name() for p in running])
    assert found_names == sorted(requested_names)

    # Assertions on the mock object remain the same
    _process_iter.assert_called_once_with(['name'])


def test_only_some_processes_found(_process_iter):
    """
    Tests that only the subset of processes that are running are returned.
    """

    from savegem.common.util.process import get_running_processes

    requested_names = ["firefox.exe", "vlc.exe", "slack.exe"]

    mock_proc_vlc = create_mock_process("vlc.exe", pid=300)

    # The iterator yields processes, but only "vlc.exe" is in the requested list
    _process_iter.return_value = [
        create_mock_process("explorer.exe"),
        mock_proc_vlc,
        create_mock_process("not_firefox.exe"),
    ]

    running = get_running_processes(requested_names)

    assert len(running) == 1
    assert running[0].name() == "vlc.exe"


def test_stop_early_optimization(_process_iter):
    """
    Tests the optimization where the loop breaks once all requested processes are found.
    This is verified by ensuring subsequent mock processes are not accessed.
    """

    from savegem.common.util.process import get_running_processes

    requested_names = ["a.exe", "b.exe"]

    mock_proc_a = create_mock_process("a.exe")
    mock_proc_b = create_mock_process("b.exe")
    mock_proc_c = create_mock_process("c.exe")  # Should not be checked

    # a.exe and b.exe are found first, followed by c.exe
    all_mock_processes = [mock_proc_a, mock_proc_b, mock_proc_c]
    _process_iter.return_value = all_mock_processes

    # We need to reset the call counts on the process that follows the break point
    mock_proc_c.name.reset_mock()

    get_running_processes(requested_names)

    # Assert that name() was called on the found processes
    mock_proc_a.name.assert_called_once()
    mock_proc_b.name.assert_called_once()

    # Assert that name() was NOT called on the subsequent process (c.exe)
    # because the loop should have broken after finding the second process.
    mock_proc_c.name.assert_not_called()


def test_handle_no_such_process(_process_iter):
    """
    Tests that NoSuchProcess exception is caught and the process is safely ignored.
    """

    from savegem.common.util.process import get_running_processes

    requested_names = ["good.exe", "bad.exe"]
    mock_proc_good = create_mock_process("good.exe", pid=101)

    # Mock a process that raises NoSuchProcess when .name() is called
    mock_proc_error = mock.Mock(spec=psutil.Process)
    mock_proc_error.name.side_effect = psutil.NoSuchProcess(1000, "proc disappeared")

    _process_iter.return_value = [
        mock_proc_error,  # This one raises an exception and should be ignored
        mock_proc_good  # This one should be found successfully
    ]

    running = get_running_processes(requested_names)

    assert len(running) == 1
    assert running[0].name() == "good.exe"


def test_handle_access_denied(_process_iter):
    """
    Tests that AccessDenied exception is caught and the process is safely ignored.
    """

    from savegem.common.util.process import get_running_processes

    requested_names = ["safe.exe", "denied.exe"]

    mock_proc_safe = create_mock_process("safe.exe", pid=201)

    # Mock a process that raises AccessDenied when .name() is called
    mock_proc_error = mock.Mock(spec=psutil.Process)
    mock_proc_error.name.side_effect = psutil.AccessDenied(2000, "permission denied")

    _process_iter.return_value = [
        mock_proc_error,  # This one raises an exception and should be ignored
        mock_proc_safe  # This one should be found successfully
    ]

    running = get_running_processes(requested_names)

    assert len(running) == 1
    assert running[0].name() == "safe.exe"


def test_empty_input_list(_process_iter):
    """
    Tests function behavior when an empty list of processes is provided
    """

    from savegem.common.util.process import get_running_processes

    # Configure the iterator with a large list to ensure it doesn't get fully consumed
    _process_iter.return_value = [
        create_mock_process("a.exe"),
        create_mock_process("b.exe")
    ]

    running = get_running_processes([])

    # When processes=[] (length 0), the loop should break immediately because
    # len(running_processes) (0) == len(processes) (0).
    assert running == []

    # The iterator is still technically called, but the inner logic (process.name())
    # should not be called if the optimization works.
    _process_iter.return_value[0].name.assert_not_called()


def test_matching_process_is_running(_system_env, _process_iter):
    """
    Tests that True is returned when an identical, *other* process is found.
    """

    from savegem.common.util.process import is_process_already_running

    process_name = "test_app"
    current_pid = 100

    mock_processes = [
        # Current process - must be ignored
        create_mock_process(process_name, pid=current_pid, exe_path=CURRENT_REAL_EXE),
        # Matching process - should cause True return
        create_mock_process(process_name, pid=500, exe_path=CURRENT_REAL_EXE),
    ]
    _process_iter.return_value = mock_processes

    assert is_process_already_running(process_name) is True

    # Check that process_iter was called with the required attributes
    _process_iter.assert_called_once_with(['name', 'pid', 'exe'])


def test_no_other_matching_process(_system_env, _process_iter):
    """
    Tests that False is returned when only non-matching or the current process is found.
    """

    from savegem.common.util.process import is_process_already_running

    process_name = "test_app"
    current_pid = 100

    mock_processes = [
        # Current process (ignored by PID)
        create_mock_process(process_name, pid=current_pid, exe_path=CURRENT_REAL_EXE),
        # Name match, EXE mismatch (ignored by EXE)
        create_mock_process(process_name, pid=200, exe_path="/usr/bin/python3"),
        # EXE match, Name mismatch (ignored by Name)
        create_mock_process("other_name", pid=300, exe_path=CURRENT_REAL_EXE),
        # Mismatch all
        create_mock_process("other_name", pid=400, exe_path="/usr/bin/other"),
    ]
    _process_iter.return_value = mock_processes

    assert is_process_already_running(process_name) is False


def test_current_process_is_ignored(_system_env, _process_iter):
    """
    Tests that the current process, even if its name matches, is correctly excluded.
    """

    from savegem.common.util.process import is_process_already_running

    process_name = "test_app"
    current_pid = 100

    mock_processes = [
        # Only the current process is running
        create_mock_process(process_name, pid=current_pid, exe_path=CURRENT_REAL_EXE),
    ]
    _process_iter.return_value = mock_processes

    assert is_process_already_running(process_name) is False


def test_handles_psutil_exceptions(_system_env, _process_iter):
    """
    Tests that NoSuchProcess and AccessDenied exceptions are caught and the search continues.
    """

    from savegem.common.util.process import is_process_already_running

    process_name = "test_app"
    current_pid = 100

    # Mock objects to raise exceptions during iteration
    mock_proc_error_1 = mock.Mock(spec=psutil.Process, pid=800)
    mock_proc_error_1.exe.return_value = CURRENT_REAL_EXE
    mock_proc_error_1.exe.side_effect = psutil.AccessDenied(800, "permission denied")

    mock_proc_error_2 = mock.Mock(spec=psutil.Process, pid=900)
    mock_proc_error_2.exe.return_value = CURRENT_REAL_EXE
    mock_proc_error_2.name.side_effect = psutil.NoSuchProcess(900, "proc disappeared")

    mock_proc_good = create_mock_process(process_name, pid=700, exe_path=CURRENT_REAL_EXE)

    mock_processes = [
        create_mock_process(process_name, pid=current_pid, exe_path=CURRENT_REAL_EXE),  # Current
        mock_proc_error_1,  # Raises AccessDenied, should be skipped
        mock_proc_error_2,  # Raises NoSuchProcess, should be skipped
        mock_proc_good,     # The matching process
    ]
    _process_iter.return_value = mock_processes

    # The function should catch exceptions and return True after finding the good process.
    assert is_process_already_running(process_name) is True


def test_empty_executable_path(_system_env, _process_iter):
    """
    Tests a process whose .exe() returns None or an empty string (e.g., some system processes).
    """

    from savegem.common.util.process import is_process_already_running

    process_name = "test_app"

    mock_processes = [
        # Process with matching name but None executable path
        create_mock_process(process_name, pid=1000, exe_path=None),
        # Process with matching name but empty executable path
        create_mock_process(process_name, pid=1001, exe_path=""),
    ]
    _process_iter.return_value = mock_processes

    # These should be filtered out by the 'if process_exe != current_exe_path' check.
    assert is_process_already_running(process_name) is False
