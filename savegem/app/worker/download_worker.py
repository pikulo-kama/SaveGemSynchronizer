from savegem.app.worker import QSubscriptableWorker
from savegem.common.core.context import app
from savegem.common.service.downloader import Downloader
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class DownloadWorker(QSubscriptableWorker):
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
        _logger.info("game=%s, file_id=%s", app().games.current.name, self.__file_id)
        downloader.download(app().games.current, file_id=self.__file_id)
