from PyQt6.QtCore import QThread

from savegem.app.gui.thread import execute_in_thread
from savegem.app.gui.widget.metadata import UISection
from savegem.app.gui.window import gui
from savegem.app.startup.worker import get_startup_workers, QStartupWorker


class StartupJob:
    """
    Used to perform all word needed for application to load main screen.
    Will initiate application UI build once all workers are finished.
    """

    def __init__(self):

        self.__startup_threads = []
        self.__finished_tasks = []

        self.__tasks = get_startup_workers()

    def start(self):
        """
        Used to start all available startup workers.
        All workers would be executed in separate threads.
        """

        gui().build(UISection.WaitSection)

        for task in self.__tasks:
            thread = QThread()

            task.link(self)
            task.finished.connect(self.__on_worker_finish(task))

            # Need to have hard reference for the thread,
            # so it won't be garbage collected.
            self.__startup_threads.append(thread)
            execute_in_thread(thread, task)

    @property
    def finished_tasks(self):
        """
        Used to get list of class names of
        tasks that have been completed.
        """
        return self.__finished_tasks

    def __on_worker_finish(self, startup_worker: QStartupWorker):
        """
        Used to get callback function that gets invoked
        each time the worker finishes its work.
        """

        def update_execution_info():
            self.__finished_tasks.append(type(startup_worker).__name__)

            # If all tasks have been finished then initiate
            # main screen build.
            if len(self.__finished_tasks) == len(self.__tasks):
                gui().build()

        return update_execution_info
