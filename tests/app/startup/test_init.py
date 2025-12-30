from unittest.mock import MagicMock, call, ANY

import pytest
from PyQt6.QtCore import pyqtSignal


class TestStartupJob:

    @pytest.fixture(autouse=True)
    def _setup(self, module_patch, _mock_tasks):
        module_patch("get_startup_workers", return_value=_mock_tasks)

    @pytest.fixture
    def _mock_startup_worker(self):
        from savegem.startup import QStartupWorker

        class MockStartupWorker(QStartupWorker):
            """
            A mock QStartupWorker that exposes its signal cleanly.
            """
            # QStartupWorker inherits QObject, which defines signals.
            # We define a dummy signal here for easy testing.
            finished = pyqtSignal()

            def __init__(self, name="Worker"):
                # We need a dummy __init__ because the base class might not be mockable
                super().__init__()
                self.__name = name
                self.link = MagicMock()

            # Expose the type name for tracking
            def __repr__(self):
                return self.__name

            @property
            def name(self):
                return self.__name

        return MockStartupWorker

    @pytest.fixture
    def _mock_tasks(self, _mock_startup_worker):
        """
        Returns a list of mock workers.
        """

        return [
            _mock_startup_worker(name="TaskOne"),
            _mock_startup_worker(name="TaskTwo"),
        ]

    def test_init_state(self, _mock_tasks):
        """
        Test initialization of internal state and task loading.
        """

        from savegem.startup import StartupJob

        job = StartupJob()

        assert job.finished_tasks == []
        assert job._StartupJob__tasks == _mock_tasks  # noqa
        assert job._StartupJob__startup_threads == []  # noqa

    def test_start_method_setup(self, _mock_tasks, gui_mock, exec_in_thread_mock, qthread_mock):
        """
        Tests that start() performs all necessary setup steps for threading and UI.
        """

        from savegem.app.gui.constants import UISection
        from savegem.startup import StartupJob

        job = StartupJob()
        job.start()

        # 1. Assert GUI build for WaitSection is called first
        gui_mock.build.assert_called_once_with(UISection.WaitSection)

        # 2. Assert correct number of threads were created and stored (preventing GC)
        assert qthread_mock.call_count == 2
        assert len(job._StartupJob__startup_threads) == 2  # noqa

        # 3. Assert tasks were linked and executed
        for task in _mock_tasks:
            task.link.assert_called_once_with(job)
            exec_in_thread_mock.assert_any_call(ANY, task)  # ANY checks the thread object

    def test_on_worker_finish_tracking(self, _mock_startup_worker):
        """
        Tests that task completion is correctly recorded.
        """

        from savegem.startup import StartupJob

        job = StartupJob()
        worker = _mock_startup_worker()

        # Get the callback function
        callback = job._StartupJob__on_worker_finish(worker)  # noqa

        callback()  # Simulate worker1 A finishing
        assert job.finished_tasks == ["Worker"]

    def test_on_worker_finish_final_build(self, gui_mock, _mock_tasks):
        """
        Tests that gui().build() is only called when ALL tasks have finished.
        """

        from savegem.startup import StartupJob

        job = StartupJob()

        # Get callbacks for both tasks
        cb_task1 = job._StartupJob__on_worker_finish(_mock_tasks[0])  # noqa
        cb_task2 = job._StartupJob__on_worker_finish(_mock_tasks[1])  # noqa

        # 1. Task 1 finishes (Not all tasks done)
        cb_task1()
        assert job.finished_tasks == ["TaskOne"]

        # 2. Task 2 finishes (All tasks done)
        cb_task2()

        # Assert gui.build() is called *again* to launch the main screen (build() without args)
        assert gui_mock.build.call_args_list[-1] == call()
        assert job.finished_tasks == ["TaskOne", "TaskTwo"]
