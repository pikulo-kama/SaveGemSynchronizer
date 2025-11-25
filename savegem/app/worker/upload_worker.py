from savegem.app.worker import QSubscriptableWorker
from savegem.common.core.context import app
from savegem.common.service.uploader import Uploader
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class UploadWorker(QSubscriptableWorker):
    """
    Worker used to upload current save
    to the drive.
    """

    def _run(self):
        uploader = Uploader()
        uploader.subscribe(self._on_subscriptable_event)

        _logger.info("Starting upload of local save to drive.")
        _logger.info("game=%s", app().games.current.name)
        uploader.upload(app().games.current)
