from threading import Thread
from savegem.app.gui.constants import TkCursor


def execute_in_thread(function):
    """
    Used to execute operation in separate thread.
    """
    Thread(target=function).start()


def execute_in_blocking_thread(function):
    """
    Used to execute operation in separate thread.

    Will update UI cursor to display that operation is being performed.
    Will block GUI while performing task.
    """

    from savegem.app.gui.window import gui

    if gui.is_blocked:
        return

    def task():
        function()
        gui.set_cursor(TkCursor.Default)
        gui.is_blocked = False

    gui.set_cursor(TkCursor.Wait)
    gui.is_blocked = True

    Thread(target=task).start()
