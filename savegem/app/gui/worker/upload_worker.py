from savegem.app.gui.worker import QSubscriptableWorker
from savegem.common.core import app
from savegem.common.service.uploader import Uploader


class UploadWorker(QSubscriptableWorker):
    """
    Worker used to upload current save
    to the drive.
    """

    def _run(self):
        uploader = Uploader()
        uploader.subscribe(self._on_subscriptable_event)

        uploader.upload(app.games.current)
