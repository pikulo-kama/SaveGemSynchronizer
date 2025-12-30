import pytest


class TestDataFetchWorkers:

    def test_current_user_worker(self, gdrive_mock, holder_mock):
        """
        Tests CurrentUserDownloadWorker calls GDrive.get_current_user and stores the result.
        """

        from savegem.startup import CurrentUserDownloadWorker
        from savegem.constants import HolderObject

        # Setup expected return value
        gdrive_mock.get_current_user.return_value = {"name": "Test User"}

        worker = CurrentUserDownloadWorker()
        worker._run()

        # 1. Assert GDrive was called
        gdrive_mock.get_current_user.assert_called_once()

        # 2. Assert result was passed to holder() with the correct key
        holder_mock.add.assert_called_once_with(
            HolderObject.CurrentUser,
            {"name": "Test User"}
        )

    def test_all_users_worker(self, gdrive_mock, app_config_mock, holder_mock):
        """
        Tests AllUsersDownloadWorker calls GDrive.get_users_with_access with the correct ID.
        """

        from savegem.startup import AllUsersDownloadWorker
        from savegem.constants import HolderObject

        # Setup expected return value
        gdrive_mock.get_users_with_access.return_value = ["user_a", "user_b"]

        worker = AllUsersDownloadWorker()
        worker._run()

        # 1. Assert GDrive was called with the config ID
        gdrive_mock.get_users_with_access.assert_called_once_with(
            app_config_mock.games_config_file_id
        )

        # 2. Assert result was passed to holder() with the correct key
        holder_mock.add.assert_called_once_with(
            HolderObject.AllUsers,
            ["user_a", "user_b"]
        )

    @pytest.mark.parametrize("class_name, file_id_attr, holder_key_name", [
        ("UserDataDownloadWorker", "users_config_file_id", "UserData"),
        ("ActivityWorker", "activity_log_file_id", "Activity"),
        ("GameConfigDownloadWorker", "games_config_file_id", "GamesConfig"),
    ])
    def test_json_download_workers(self, holder_mock, app_config_mock, class_name, file_id_attr, holder_key_name):
        """
        Tests that JSON download workers call holder().download_json with the correct file ID
        obtained from app().config.
        """

        from savegem.constants import HolderObject
        import savegem.startup.worker1.data as data_module

        worker_class = getattr(data_module, class_name)
        expected_holder_key = getattr(HolderObject, holder_key_name)

        # Get the expected file ID from the mocked config object
        expected_file_id = getattr(app_config_mock, file_id_attr)

        worker = worker_class()
        worker._run()

        # Assert holder().download_json was called once
        holder_mock.download_json.assert_called_once()

        # Assert the arguments are the correct key and the correct file ID
        holder_mock.download_json.assert_called_once_with(
            expected_holder_key,
            expected_file_id
        )
