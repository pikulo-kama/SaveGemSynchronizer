

class TestInitializationWorker:

    def test_dependencies(self):
        """
        Tests that the dependencies list is fully and correctly defined,
        ensuring this worker1 runs last.
        """

        from savegem.app.startup import InitializationWorker
        from savegem.app.startup import ActivityWorker, GameConfigDownloadWorker, \
            CurrentUserDownloadWorker, AllUsersDownloadWorker, UserDataDownloadWorker

        worker = InitializationWorker()
        expected_dependencies = [
            ActivityWorker.__name__,
            GameConfigDownloadWorker.__name__,
            CurrentUserDownloadWorker.__name__,
            AllUsersDownloadWorker.__name__,
            UserDataDownloadWorker.__name__
        ]

        # Ensure the list order and content match
        assert worker.dependencies == expected_dependencies

    def test_run_method_calls(self, games_config_mock, user_config_mock, app_state_mock, activity_mock):
        """
        Tests that _run() calls all required initialization, refresh, and checksum
        methods on the global app context.
        """

        from savegem.app.startup import InitializationWorker

        worker = InitializationWorker()
        worker._run()

        user_config_mock.initialize.assert_called_once()
        app_state_mock.refresh.assert_called_once()
        games_config_mock.initialize.assert_called_once()

        # 2. Assert iteration over games occurred
        games_config_mock.__iter__.assert_called_once()

        # 3. Assert metadata calculations were performed for each game
        # Since we mocked one game, we check calls on the mocked metadata objects
        games_config_mock.first.meta.local.calculate_checksum.assert_called_once()
        games_config_mock.first.meta.drive.refresh.assert_called_once()

        games_config_mock.second.meta.local.calculate_checksum.assert_called_once()
        games_config_mock.second.meta.drive.refresh.assert_called_once()

        # 4. Assert final activity refresh
        activity_mock.refresh.assert_called_once()
