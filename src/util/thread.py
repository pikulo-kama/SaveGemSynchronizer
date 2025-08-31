from threading import Thread
from src.gui import gui
from src.gui.constants import TkCursor


def execute_in_thread(function):
    """
    Used to execute operation in separate thread.
    Will update UI cursor to display that operation is being performed.
    """

    if gui.is_blocked:
        return

    def task():
        function()
        gui.set_cursor()
        gui.is_blocked = False

    gui.set_cursor(TkCursor.Wait)
    gui.is_blocked = True

    Thread(target=task).start()
