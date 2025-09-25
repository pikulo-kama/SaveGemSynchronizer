from PyQt6.QtCore import Qt, QThread
from savegem.app.gui.worker import QWorker
from savegem.app.gui.window import gui


def execute_in_blocking_thread(thread: QThread, worker: QWorker):
    """
    Used to execute operation in separate thread.

    Will update UI cursor to display that operation is being performed.
    Will block GUI while performing task.
    """

    if gui().is_blocked:
        return

    def on_finish():
        gui().setCursor(Qt.CursorShape.ArrowCursor)
        gui().is_blocked = False

    worker.moveToThread(thread)

    worker.completed.connect(thread.quit)  # noqa
    thread.finished.connect(worker.deleteLater)  # noqa
    thread.finished.connect(thread.deleteLater)  # noqa
    thread.finished.connect(on_finish)  # noqa

    thread.started.connect(worker.start)  # noqa
    thread.start()

    gui().setCursor(Qt.CursorShape.WaitCursor)
    gui().is_blocked = True
