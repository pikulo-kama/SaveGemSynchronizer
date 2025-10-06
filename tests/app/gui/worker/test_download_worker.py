

def test_download_worker_run_logic(downloader_mock, app_context, games_config):
    """
    Test that _run() instantiates Downloader, subscribes the handler,
    and calls download with the current game.
    """

    from savegem.app.gui.worker.download_worker import DownloadWorker

    worker = DownloadWorker()
    expected_handler = worker._on_subscriptable_event

    worker._run()

    downloader_mock.assert_called_once_with()
    downloader_mock.return_value.subscribe.assert_called_once_with(expected_handler)

    downloader_mock.return_value.download.assert_called_once_with(
        games_config.current
    )
