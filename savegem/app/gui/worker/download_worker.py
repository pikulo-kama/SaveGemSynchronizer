from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.window import gui
from savegem.app.gui.worker import QSubscriptableWorker
from savegem.common.core import app
from savegem.common.service.downloader import Downloader


class DownloadWorker(QSubscriptableWorker):
    """
    Worker used to download last save
    from drive.
    """

    def _run(self):
        downloader = Downloader()
        downloader.subscribe(self._on_subscriptable_event)

        downloader.download(app.games.current)
