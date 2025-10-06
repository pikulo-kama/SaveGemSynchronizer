

def test_game_change_worker_run_logic(app_context, app_state_mock, games_config, activity_mock):
    """
    Test that _run() correctly updates 'app.state', refreshes drive metadata,
    and refreshes activity.
    """

    from savegem.app.gui.worker.game_change_worker import GameChangeWorker

    test_game_name = "Test"
    worker = GameChangeWorker(test_game_name)

    worker._run()

    assert app_state_mock.game_name == test_game_name
    games_config.current.meta.drive.refresh.assert_called_once()
    activity_mock.refresh.assert_called_once()
