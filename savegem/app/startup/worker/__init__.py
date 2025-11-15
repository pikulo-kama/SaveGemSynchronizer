import time
from typing import Optional, TYPE_CHECKING

from savegem.app.worker import QWorker
from savegem.common.util.reflection import get_members

if TYPE_CHECKING:
    from savegem.app.startup import StartupJob


def get_startup_workers() -> list["QStartupWorker"]:
    """
    Used to get list of all startup workers
    defined in current package.
    """

    members = []

    for _, member in get_members(__package__, QStartupWorker):
        members.append(member())

    return members


class QStartupWorker(QWorker):
    """
    Represents worker that is used for startup operations.
    """

    def __init__(self):
        QWorker.__init__(self)
        self.__job: Optional["StartupJob"] = None

    def start(self):
        """
        Used to start worker.

        If worker has dependencies that haven't finished yet
        then current worker will wait until they're finished.
        """

        while self.__has_unfinished_dependencies():
            # Wait 50ms before retrying.
            time.sleep(0.05)

        super().start()

    def link(self, job: "StartupJob"):
        """
        Used to link startup worker to the
        startup job.
        """
        self.__job = job

    @property
    def dependencies(self) -> list[str]:
        """
        Used to get list of worker names
        current worker depends on.
        """
        return []

    def __has_unfinished_dependencies(self):
        """
        Used to check if all dependency workers
        finished its work.
        """

        for dependency in self.dependencies:
            if dependency not in self.__job.finished_tasks:
                return True

        return False
