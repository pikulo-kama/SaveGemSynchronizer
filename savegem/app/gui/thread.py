from typing import TYPE_CHECKING
from PyQt6.QtCore import Qt, QThread

if TYPE_CHECKING:
    from savegem.app.worker import QWorker


def execute_in_blocking_thread(thread: QThread, worker: "QWorker"):
    """
    Used to execute operation in separate thread.

    Will update UI cursor to display that operation is being performed.
    Will block GUI while performing task.
    """

    from savegem.app.gui.window import gui

    if gui().is_blocked:
        return

    def on_finish():
        gui().setCursor(Qt.CursorShape.ArrowCursor)
        gui().is_blocked = False

    thread.finished.connect(on_finish)  # noqa
    execute_in_thread(thread, worker)

    gui().setCursor(Qt.CursorShape.WaitCursor)
    gui().is_blocked = True


def execute_in_thread(thread: QThread, worker: "QWorker"):

    worker.moveToThread(thread)

    worker.finished.connect(thread.quit)  # noqa
    thread.finished.connect(worker.deleteLater)  # noqa
    thread.finished.connect(thread.deleteLater)  # noqa

    thread.started.connect(worker.start)  # noqa
    thread.start()
