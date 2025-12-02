from unittest.mock import MagicMock, call
import pytest
from pytest_mock import MockerFixture


class TestQStartupWorker:

    @pytest.fixture(autouse=True)
    def _setup(self, get_members_mock, _worker_a, _worker_b, _worker_c):
        def mock_get_members(_, __):
            yield _worker_a.__name__, _worker_a
            yield _worker_b.__name__, _worker_b
            yield _worker_c.__name__, _worker_c

        get_members_mock.side_effect = mock_get_members

    @pytest.fixture
    def _base_start_mock(self, mocker: MockerFixture):
        from savegem.app.worker import QWorker
        return mocker.patch.object(QWorker, "start")

    @pytest.fixture
    def _worker_a(self):
        from savegem.app.startup import QStartupWorker

        class WorkerA(QStartupWorker):
            pass

        return WorkerA

    @pytest.fixture
    def _worker_b(self):
        from savegem.app.startup import QStartupWorker

        class WorkerB(QStartupWorker):
            @property
            def dependencies(self) -> list[str]:
                return ["WorkerA"]  # Depends on WorkerA

        return WorkerB

    @pytest.fixture
    def _worker_c(self):
        from savegem.app.startup import QStartupWorker

        class WorkerC(QStartupWorker):
            @property
            def dependencies(self) -> list[str]:
                return ["NonExistent"]

        return WorkerC

    @pytest.fixture
    def _startup_job_mock(self, mocker: MockerFixture):
        return mocker.MagicMock()

    def test_get_startup_workers_reflection(self, _worker_a, _worker_b, _worker_c):
        """
        Tests that all subclasses are correctly found and instantiated.
        """

        from savegem.app.startup import get_startup_workers

        workers = get_startup_workers()

        # We expect 3 workers based on our mock_get_members setup
        assert len(workers) == 3
        assert isinstance(workers[0], _worker_a)
        assert isinstance(workers[1], _worker_b)
        assert isinstance(workers[2], _worker_c)

    def test_init_and_link(self, _worker_a, _startup_job_mock):
        """
        Test initialization and linking to the job.
        """

        from savegem.app.startup import QStartupWorker

        worker = _worker_a()

        assert isinstance(worker, QStartupWorker)
        assert worker.name == "WorkerA"
        assert worker.dependencies == []

        # Test link method
        mock_job = _startup_job_mock([])
        worker.link(mock_job)
        assert worker._QStartupWorker__job == mock_job  # noqa

    def test_has_unfinished_dependencies_false(self, _worker_b, _startup_job_mock):
        """
        Test case where all dependencies are finished.
        """

        worker = _worker_b()  # Depends on WorkerA

        # Job shows dependency is finished
        _startup_job_mock.finished_tasks = ["WorkerA", "SomeOtherTask"]
        worker.link(_startup_job_mock)  # noqa

        # Access the private method via name mangling
        assert worker._QStartupWorker__has_unfinished_dependencies() is False  # noqa

    def test_has_unfinished_dependencies_true(self, _worker_b, _startup_job_mock):
        """
        Test case where a dependency is missing from the finished list.
        """

        worker = _worker_b()

        # Job only has other finished tasks, not WorkerA
        _startup_job_mock.finished_tasks = ["SomeOtherTask"]
        worker.link(_startup_job_mock)

        assert worker._QStartupWorker__has_unfinished_dependencies() is True  # noqa

    def test_start_no_dependencies(self, _base_start_mock, _worker_a, _startup_job_mock, time_sleep_mock):
        """
        Test start() when there are no dependencies (should run immediately).
        """

        _startup_job_mock.finished_tasks = []

        worker = _worker_a()
        worker.link(_startup_job_mock)

        worker.start()

        # Should call QWorker.start() immediately
        _base_start_mock.assert_called_once()
        time_sleep_mock.assert_not_called()

    def test_start_dependencies_finished_immediately(self, _worker_b, _startup_job_mock, _base_start_mock,
                                                     time_sleep_mock):
        """
        Test start() when dependencies are already met (should run immediately).
        """

        _startup_job_mock.finished_tasks = ["WorkerA"]

        worker = _worker_b()  # Depends on WorkerA
        worker.link(_startup_job_mock)

        worker.start()

        _base_start_mock.assert_called_once()
        time_sleep_mock.assert_not_called()

    def test_start_dependencies_wait_and_run(self, _worker_b, _base_start_mock, _startup_job_mock, time_sleep_mock):
        """
        Test the busy-wait loop logic (worker sleeps, then runs).
        """

        _startup_job_mock.finished_tasks = []

        worker = _worker_b()  # Depends on WorkerA
        worker.link(_startup_job_mock)

        # Mock the internal dependency check to fail twice, then pass
        # This simulates the dependency finishing while the loop is running.
        worker._QStartupWorker__has_unfinished_dependencies = MagicMock(side_effect=[True, True, False])

        worker.start()

        # Assert the loop ran 3 times (True, True, False)
        assert worker._QStartupWorker__has_unfinished_dependencies.call_count == 3

        # Assert sleep was called twice
        assert time_sleep_mock.call_count == 2
        time_sleep_mock.assert_has_calls([call(0.05), call(0.05)])

        _base_start_mock.assert_called_once()
