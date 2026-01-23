from kutil.logger import get_logger

from src.savegem.app.worker import SubscriptableWorker
from src.savegem.common.core.context import context
from src.savegem.common.service.downloader import Downloader


_logger = get_logger(__name__)


class DownloadWorker(SubscriptableWorker):
    """
    Worker used to download save
    from drive.

    If file ID is not provided then latest save
    would be downloaded.
    """

    def __init__(self, file_id: str = None):
        super().__init__()
        self.__file_id = file_id

    def _run(self):
        downloader = Downloader()
        downloader.subscribe(self._on_subscriptable_event)

        _logger.info("Starting download of save from drive.")
        _logger.info("game=%s, file_id=%s", context().games.current.name, self.__file_id)
        downloader.download(context().games.current, file_id=self.__file_id)
