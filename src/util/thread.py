from threading import Thread
from src.gui import gui


def execute_in_thread(function):
    """
    Used to execute operation in separate thread.
    Will update UI cursor to display that operation is being performed.
    """

    def task():
        function()
        gui.set_cursor()

    gui.set_cursor("wait")
    Thread(target=task).start()
