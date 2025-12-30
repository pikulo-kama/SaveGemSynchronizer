

class TestGameChangeWorker:

    def test_game_change_worker_run_logic(self, app_context_mock, app_state_mock, games_config_mock, activity_mock):
        """
        Test that _run() correctly updates 'app.state', refreshes drive metadata,
        and refreshes activity.
        """

        from savegem.worker.game_change_worker import GameChangeWorker

        test_game_name = "Test"
        worker = GameChangeWorker(test_game_name)

        worker._run()

        assert app_state_mock.game_name == test_game_name
        activity_mock.refresh.assert_called_once()
