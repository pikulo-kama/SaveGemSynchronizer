import pytest
from pytest_mock import MockerFixture

from savegem.app.gui.worker import QSubscriptableWorker, QWorker
from savegem.common.service.subscriptable import ErrorEvent, ProgressEvent, Event, DoneEvent


@pytest.fixture
def _subscriptable_worker(_error_callback, _progress_callback, _completed_callback):
    """
    Provides an instance of QSubscriptableWorker.
    """

    worker = QSubscriptableWorker()
    # Mock _run to prevent NotImplementedError if start() were called
    worker._run = lambda: None

    worker.error.connect(_error_callback)
    worker.progress.connect(_progress_callback)
    worker.completed.connect(_completed_callback)

    return worker


@pytest.fixture
def _error_callback(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def _progress_callback(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def _completed_callback(mocker: MockerFixture):
    return mocker.Mock()


def test_qworker_abstract_method(gui_mock):
    """
    Test that calling _run() on the base QWorker raises NotImplementedError.
    """

    with pytest.raises(NotImplementedError):
        QWorker()._run()


def test_qworker_start_success(mocker: MockerFixture, gui_mock):
    """
    Test start() correctly calls _run, emits finished, and handles mutex locks.
    """

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

    # Assert 1: Mutex locking/unlocking
    gui_mock.mutex.lock.assert_called_once()
    gui_mock.mutex.unlock.assert_called_once()

    # Assert 2: _run execution
    assert worker.ran is True

    # Assert 3: Signal emission
    finished_callback.assert_called_once_with()


def test_qworker_start_failure_mutex_release(mocker: MockerFixture, gui_mock):
    """
    Test that start() releases the mutex even if _run() raises an exception,
    and finished is NOT emitted.
    """

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

    # Assert 2: Mutex unlocking (crucial for thread safety)
    gui_mock.mutex.lock.assert_called_once()
    gui_mock.mutex.unlock.assert_called_once()

    # Assert 3: finished signal should NOT be emitted
    finished_callback.assert_not_called()


def test_subscriptable_worker_event_error(_subscriptable_worker, _error_callback, _progress_callback,
                                          _completed_callback):
    """
    Test ErrorEvent is correctly propagated via the error signal.
    """

    error_event = ErrorEvent("Test Error")

    _subscriptable_worker._on_subscriptable_event(error_event)

    _error_callback.assert_called_once_with(error_event)
    _progress_callback.assert_not_called()
    _completed_callback.assert_not_called()


def test_subscriptable_worker_event_progress(_subscriptable_worker, _error_callback, _progress_callback,
                                             _completed_callback):
    """
    Test ProgressEvent is correctly propagated via the progress signal.
    """

    progress_event = ProgressEvent(None, 50)

    _subscriptable_worker._on_subscriptable_event(progress_event)

    _progress_callback.assert_called_once_with(progress_event)
    _error_callback.assert_not_called()
    _completed_callback.assert_not_called()


def test_subscriptable_worker_event_done(_subscriptable_worker, _error_callback, _progress_callback,
                                         _completed_callback):
    """
    Test DoneEvent is correctly propagated via the completed signal.
    """

    done_event = DoneEvent(None)

    _subscriptable_worker._on_subscriptable_event(done_event)

    _completed_callback.assert_called_once_with(done_event)
    _error_callback.assert_not_called()
    _progress_callback.assert_not_called()


def test_subscriptable_worker_event_unhandled(_subscriptable_worker, _error_callback, _progress_callback,
                                              _completed_callback):
    """
    Test an unhandled Event type is ignored.
    """

    unhandled_event = Event(None)

    _subscriptable_worker._on_subscriptable_event(unhandled_event)

    _error_callback.assert_not_called()
    _progress_callback.assert_not_called()
    _completed_callback.assert_not_called()
