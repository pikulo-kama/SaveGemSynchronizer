import pytest
from pytest_mock import MockerFixture


class TestQWorker:

    def test_qworker_abstract_method(self, gui_mock):
        """
        Test that calling _run() on the base QWorker raises NotImplementedError.
        """

        from savegem.app.worker import QWorker

        with pytest.raises(NotImplementedError):
            QWorker()._run()

    def test_qworker_start_success(self, mocker: MockerFixture, gui_mock):
        """
        Test start() correctly calls _run, emits finished, and handles mutex locks.
        """

        from savegem.app.worker import QWorker

        class ConcreteWorker(QWorker):
            def _run(self):
                self.ran = True

        worker = ConcreteWorker()
        worker.ran = False

        # Spy on the finished signal emitter
        finished_callback = mocker.Mock()
        worker.finished.connect(finished_callback)

        # Act
        worker.start()

        # Assert 2: _run execution
        assert worker.ran is True

        # Assert 3: Signal emission
        finished_callback.assert_called_once_with()

    def test_qworker_start_failure(self, mocker: MockerFixture, gui_mock):
        """
        Test that start() finished is NOT emitted if _run raises an exception.
        """

        from savegem.app.worker import QWorker

        # Arrange: Worker that always fails
        class FailingWorker(QWorker):
            def _run(self):
                raise ValueError("Simulated worker error")

        worker = FailingWorker()

        # Spy on the finished signal emitter
        finished_callback = mocker.Mock()
        worker.finished.connect(finished_callback)

        # Act and Assert 1: Check that the worker raises the error
        with pytest.raises(ValueError, match="Simulated worker error"):
            worker.start()

        # Assert 3: finished signal should NOT be emitted
        finished_callback.assert_not_called()


class TestQSubscriptableWorker:

    @pytest.fixture
    def _subscriptable_worker(self, _error_callback, _progress_callback, _completed_callback):
        """
        Provides an instance of QSubscriptableWorker.
        """

        from savegem.app.worker import QSubscriptableWorker

        worker = QSubscriptableWorker()
        # Mock _run to prevent NotImplementedError if start() were called
        worker._run = lambda: None

        worker.error.connect(_error_callback)
        worker.progress.connect(_progress_callback)
        worker.completed.connect(_completed_callback)

        return worker


    @pytest.fixture
    def _error_callback(self, mocker: MockerFixture):
        return mocker.Mock()


    @pytest.fixture
    def _progress_callback(self, mocker: MockerFixture):
        return mocker.Mock()


    @pytest.fixture
    def _completed_callback(self, mocker: MockerFixture):
        return mocker.Mock()

    def test_subscriptable_worker_event_error(self, _subscriptable_worker, _error_callback, _progress_callback,
                                              _completed_callback):
        """
        Test ErrorEvent is correctly propagated via the error signal.
        """

        from savegem.common.service.subscriptable import ErrorEvent

        error_event = ErrorEvent("Test Error")

        _subscriptable_worker._on_subscriptable_event(error_event)

        _error_callback.assert_called_once_with(error_event)
        _progress_callback.assert_not_called()
        _completed_callback.assert_not_called()


    def test_subscriptable_worker_event_progress(self, _subscriptable_worker, _error_callback, _progress_callback,
                                                 _completed_callback):
        """
        Test ProgressEvent is correctly propagated via the progress signal.
        """

        from savegem.common.service.subscriptable import ProgressEvent

        progress_event = ProgressEvent(None, 50)

        _subscriptable_worker._on_subscriptable_event(progress_event)

        _progress_callback.assert_called_once_with(progress_event)
        _error_callback.assert_not_called()
        _completed_callback.assert_not_called()


    def test_subscriptable_worker_event_done(self, _subscriptable_worker, _error_callback, _progress_callback,
                                             _completed_callback):
        """
        Test DoneEvent is correctly propagated via the completed signal.
        """

        from savegem.common.service.subscriptable import DoneEvent

        done_event = DoneEvent(None)

        _subscriptable_worker._on_subscriptable_event(done_event)

        _completed_callback.assert_called_once_with(done_event)
        _error_callback.assert_not_called()
        _progress_callback.assert_not_called()


    def test_subscriptable_worker_event_unhandled(self, _subscriptable_worker, _error_callback, _progress_callback,
                                                  _completed_callback):
        """
        Test an unhandled Event type is ignored.
        """

        from savegem.common.service.subscriptable import Event

        unhandled_event = Event(None)

        _subscriptable_worker._on_subscriptable_event(unhandled_event)

        _error_callback.assert_not_called()
        _progress_callback.assert_not_called()
        _completed_callback.assert_not_called()
