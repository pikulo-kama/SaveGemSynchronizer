from kutil.logger import get_logger

from savegem.app.worker import SubscriptableWorker
from savegem.common.core.context import context
from savegem.common.service.uploader import Uploader


_logger = get_logger(__name__)


class UploadWorker(SubscriptableWorker):
    """
    Worker used to upload current save
    to the drive.
    """

    def _run(self):
        uploader = Uploader()
        uploader.subscribe(self._on_subscriptable_event)

        _logger.info("Starting upload of local save to drive.")
        _logger.info("game=%s", context().games.current.name)
        uploader.upload(context().games.current)
