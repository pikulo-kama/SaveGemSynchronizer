from PyQt6.QtCore import QObject, pyqtSignal

from savegem.app.gui.window import gui
from savegem.common.service.subscriptable import ErrorEvent, ProgressEvent, Event, DoneEvent


class QWorker(QObject):
    """
    Represents worker that
    performs single operation
    and emits events.
    """

    completed = pyqtSignal()

    def start(self):
        """
        Worker entry point.
        """

        gui().mutex.lock()

        try:
            self._run()
        finally:
            gui().mutex.unlock()

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

    def _on_subscriptable_event(self, event: Event):
        """
        Callback function that will handle events
        from subscriptable service and propagate them
        to worker signal objects.
        """

        if isinstance(event, ErrorEvent):
            self.error.emit(event)  # noqa

        elif isinstance(event, ProgressEvent):
            self.progress.emit(event)  # noqa

        elif isinstance(event, DoneEvent):
            self.completed.emit()  # noqa
