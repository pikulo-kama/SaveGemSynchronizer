from threading import Thread
from src.gui.gui import GUI


def execute_in_thread(function):
    """
    Used to execute operation in separate thread.
    Will update UI cursor to display that operation is being performed.
    """

    window = GUI.instance()

    def task():
        function()
        window.set_cursor()

    window.set_cursor("wait")
    Thread(target=task).start()
