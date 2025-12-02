from datetime import datetime
import pytest


class TestSaveInfoResolver:
    NA_LABEL = "Translated(label_NA)"

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock, module_patch):

        module_patch("get_verbose_date", return_value="Jan 15th, 2025")
        module_patch("get_verbose_time", return_value="10:30 AM")
        module_patch(
            "string_to_date",
            side_effect=lambda _: datetime(2025, 1, 15, 10, 30, 0)
        )

    @pytest.fixture
    def _resolver(self, tr_mock):
        """
        Provides the SaveInfoResolver instance.
        """

        from savegem.app.gui.widget.resolver.save_info import SaveInfoResolver
        return SaveInfoResolver()

    @pytest.fixture
    def _set_present_save(self, user_config_mock, games_config_mock):
        """
        Sets up a fully populated save context.
        """

        from savegem.common.core.save_meta import SyncStatus

        # Setup users
        user_config_mock.by_email.return_value.email = "owner@example.com"
        user_config_mock.by_email.return_value.short_name = "John"
        user_config_mock.by_email.return_value.photo = "john.jpg"

        # Setup game meta
        games_config_mock.current.meta.sync_status = SyncStatus.NeedsUpload
        games_config_mock.current.meta.drive.is_present = True
        games_config_mock.current.meta.drive.owner = "owner@example.com"
        games_config_mock.current.meta.drive.created_time = "2025-01-15T10:30:00Z"
        games_config_mock.current.meta.drive.size = 1536000  # 1.5 MB

    @pytest.fixture
    def _set_absent_save(self, games_config_mock):
        """
        Sets up a context where the save is not present (is_present=False).
        """

        from savegem.common.core.save_meta import SyncStatus

        games_config_mock.current.meta.sync_status = SyncStatus.NoInformation
        games_config_mock.current.meta.drive.is_present = False

    def test_resolve_size_megabytes(self, _resolver, _set_present_save):
        """
        Tests size calculation for > 1MB.
        """

        # Size is 1536000 bytes (1536000 // 1024 = 1500 KB)
        assert _resolver.resolve("size") == "Translated(label_SizeMegabytes, 1500)"

    def test_resolve_size_kilobytes(self, _resolver, _set_present_save, games_config_mock):
        """
        Tests size calculation for < 1KB.
        """

        games_config_mock.current.meta.drive.size = 500  # 500 bytes
        assert _resolver.resolve("size") == "Translated(label_SizeKilobytes, 500)"

    def test_resolve_upload_date(self, _resolver, _set_present_save):
        """
        Tests resolution of date string.
        """
        assert _resolver.resolve("uploadDate") == "Jan 15th, 2025"

    def test_resolve_upload_time(self, _resolver, _set_present_save):
        """
        Tests resolution of time string.
        """
        assert _resolver.resolve("uploadTime") == "10:30 AM"

    def test_resolve_owner_name(self, _resolver, _set_present_save):
        """
        Tests resolution of owner short name.
        """
        assert _resolver.resolve("ownerName") == "John"

    def test_resolve_owner_photo(self, _resolver, _set_present_save):
        """
        Tests resolution of owner photo URL.
        """
        assert _resolver.resolve("ownerPhoto") == "john.jpg"

    def test_resolve_sync_status(self, _resolver, _set_present_save):
        """
        Tests resolution of sync status label (using the setup default: NeedsUpload).
        """
        assert _resolver.resolve("status") == "Translated(info_SaveNeedsToBeUploaded)"

    def test_resolve_status_description(self, _resolver, _set_present_save):
        """
        Tests resolution of sync status description.
        """
        assert _resolver.resolve("statusDescription") == "Translated(info_SaveNeedsToBeUploadedDesc)"

    def test_resolve_status_icon(self, _resolver, _set_present_save):
        """
        Tests resolution of sync status icon.
        """
        assert _resolver.resolve("statusIcon") == "upload_warning.svg"

    @pytest.mark.parametrize("key", ["size", "uploadDate", "ownerName"])
    def test_resolve_absent_properties_return_na(self, _resolver, _set_absent_save, key):
        assert _resolver.resolve(key) == self.NA_LABEL

    @pytest.mark.parametrize("key, expected_default", [
        ("uploadTime", None),  # Time returns None, not NA, if date info is missing
        ("ownerPhoto", "person.svg"),
    ])
    def test_resolve_absent_properties_return_default(self, _resolver, _set_absent_save, key, expected_default):
        """
        Test properties that return a default/None when metadata is absent.
        """
        assert _resolver.resolve(key) == expected_default

    def test_resolve_size_negative_returns_na(self, _resolver, _set_present_save, games_config_mock):
        """
        Test that negative size returns NA.
        """

        games_config_mock.current.meta.drive.size = -10
        assert _resolver.resolve("size") == self.NA_LABEL

    def test_resolve_absent_owner_returns_default_photo(self, _resolver, _set_present_save, user_config_mock):
        """
        Test that missing user object returns default photo and NA name.
        """

        user_config_mock.by_email.return_value = None  # No user found

        assert _resolver.resolve("ownerName") == self.NA_LABEL
        assert _resolver.resolve("ownerPhoto") == "person.svg"

    @pytest.mark.parametrize("status_name, expected_label_key, expected_icon", [
        ("LocalOnly", "label_StorageIsEmpty", "upload_warning.svg"),
        ("NoInformation", "label_NoInformationStatus", "exclamation_mark.svg"),
        ("NeedsDownload", "info_SaveNeedsToBeDownloaded", "download_warning.svg"),
        ("NeedsUpload", "info_SaveNeedsToBeUploaded", "upload_warning.svg"),
    ])
    def test_resolve_all_sync_statuses(self, _resolver, games_config_mock, status_name, expected_label_key,
                                       expected_icon):
        """
        Tests all permutations of SyncStatus mapping.
        """

        from savegem.common.core.save_meta import SyncStatus

        # Configure the context for the specific status
        games_config_mock.current.meta.sync_status = SyncStatus[status_name]

        # We need a drive metadata object, but its content doesn't matter for status checks
        games_config_mock.current.meta.drive.is_present = True

        # Assert Label
        assert _resolver.resolve("status") == f"Translated({expected_label_key})"

        # Assert Description (uses same mapping logic as status, just different map)
        assert _resolver.resolve("statusDescription") == f"Translated({expected_label_key}Desc)"

        # Assert Icon
        assert _resolver.resolve("statusIcon") == expected_icon

    def test_resolve_unknown_key(self, _resolver):
        """
        Test that an unrecognized key returns label_NA.
        """
        assert _resolver.resolve("unknownKey") == self.NA_LABEL
