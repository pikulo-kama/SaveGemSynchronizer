from PyQt6.QtCore import QObject, pyqtSignal
from savegem.common.service.subscriptable import ErrorEvent, ProgressEvent, Event, DoneEvent
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class QWorker(QObject):
    """
    Represents worker that
    performs single operation
    and emits events.
    """

    finished = pyqtSignal()

    def start(self):
        """
        Worker entry point.
        """

        from savegem.app.gui.window import gui
        gui().mutex.lock()
        _logger.info("UI application has been locked.")

        try:
            _logger.info("Starting worker.")
            self._run()

            self.finished.emit()  # noqa
            _logger.info("Worker has finished its work.")
        finally:
            gui().mutex.unlock()
            _logger.info("UI application has been unlocked.")

    def _run(self):
        """
        Should be overridden by child classes.
        Contains main worker logic.
        """
        raise NotImplementedError()


class QSubscriptableWorker(QWorker):
    """
    Represents worker that works with
    subscriptable services.
    """

    error = pyqtSignal(ErrorEvent)
    progress = pyqtSignal(ProgressEvent)
    completed = pyqtSignal(DoneEvent)

    def _on_subscriptable_event(self, event: Event):
        """
        Callback function that will handle events
        from subscriptable service and propagate them
        to worker signal objects.
        """

        if isinstance(event, ErrorEvent):
            _logger.debug("Received error event from subscriptable service. Kind=%s", event.kind)
            self.error.emit(event)  # noqa

        elif isinstance(event, ProgressEvent):
            _logger.debug("Received progress event from subscriptable service. Progress=%s", event.progress)
            self.progress.emit(event)  # noqa

        elif isinstance(event, DoneEvent):
            _logger.debug("Received done event from subscriptable service. ErrorKind=%s", event.kind)
            self.completed.emit(event)  # noqa
