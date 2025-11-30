

def test_download_worker_run_logic(uploader_mock, app_context_mock, games_config_mock):
    """
    Test that _run() instantiates Downloader, subscribes the handler,
    and calls download with the current game.
    """

    from savegem.app.worker import UploadWorker

    worker = UploadWorker()
    expected_handler = worker._on_subscriptable_event

    worker._run()

    uploader_mock.assert_called_once_with()
    uploader_mock.return_value.subscribe.assert_called_once_with(expected_handler)

    uploader_mock.return_value.upload.assert_called_once_with(
        games_config_mock.current
    )
