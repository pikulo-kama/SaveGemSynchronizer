from PyQt6.QtCore import pyqtSignal
from kui.core.worker import KamaWorker
from kutil.logger import get_logger

from savegem.common.service.subscriptable import ErrorEvent, ProgressEvent, Event, DoneEvent


_logger = get_logger(__name__)


class SubscriptableWorker(KamaWorker):
    """
    Represents worker1 that works with
    subscriptable services.
    """

    error = pyqtSignal(ErrorEvent)
    progress = pyqtSignal(ProgressEvent)
    completed = pyqtSignal(DoneEvent)

    def _on_subscriptable_event(self, event: Event):
        """
        Callback function that will handle events
        from subscriptable service and propagate them
        to worker1 signal objects.
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
