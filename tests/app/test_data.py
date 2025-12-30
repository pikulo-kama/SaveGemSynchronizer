
import pytest
import json
from io import BytesIO

from tests.util import json_to_bytes_io


class TestDataHolder:

    def test_holder_is_singleton(self):
        """
        Test that the global holder() function returns a singleton instance
        (the same object) on multiple calls.
        """

        from savegem.constants import holder, DataHolder

        # 1. First call creates the instance
        holder1 = holder()

        # 2. Second call should return the same instance
        holder2 = holder()

        assert isinstance(holder1, DataHolder)
        assert holder1 is holder2

    def test_add_and_get(self):
        """
        Test basic storage and retrieval of data.
        """

        from savegem.constants import HolderObject, DataHolder

        test_data = {"key": "value", "count": 100}

        # Add
        data_holder = DataHolder()
        data_holder.add(HolderObject.CurrentUser, test_data)

        # Get
        retrieved_data = data_holder.get(HolderObject.CurrentUser)

        assert retrieved_data == test_data
        assert data_holder.get("nonExistent") is None


    def test_download_json_success(self, gdrive_mock):
        """
        Test successful download and JSON deserialization.
        """

        from savegem.constants import HolderObject, DataHolder

        test_json_data = {"setting": "active"}
        gdrive_mock.download_file.return_value.__enter__.return_value = json_to_bytes_io(test_json_data)

        # ACT
        data_holder = DataHolder()
        data_holder.download_json(HolderObject.GamesConfig, "file_id_123")

        # ASSERT
        gdrive_mock.download_file.assert_called_once_with("file_id_123")
        stored_data = data_holder.get(HolderObject.GamesConfig)

        # Check that the deserialized JSON object was stored
        assert stored_data == test_json_data


    def test_download_json_file_bytes_is_none(self, gdrive_mock):
        """
        Test case where GDrive fails to return file bytes (e.g., file not found).
        """

        from savegem.constants import HolderObject, DataHolder

        gdrive_mock.download_file.return_value.__enter__.return_value = None

        data_holder = DataHolder()
        data_holder.download_json(HolderObject.Activity, "non_existent_id")

        gdrive_mock.download_file.assert_any_call("non_existent_id")
        assert data_holder.get(HolderObject.Activity) is None


    def test_download_json_empty_file_fails_gracefully(self, gdrive_mock):
        """
        Test case where GDrive returns an empty file stream, resulting in a JSONDecodeError.
        The current implementation assumes the JSON error will be handled by the caller,
        but we verify the process up until the JSON failure.
        """

        from savegem.constants import HolderObject, DataHolder

        # Mock GDrive to return an empty stream
        mock_file_stream = BytesIO(b'')
        gdrive_mock.download_file.return_value.__enter__.return_value = mock_file_stream

        # We expect json.load to fail on an empty stream
        with pytest.raises(json.JSONDecodeError):
            data_holder = DataHolder()
            data_holder.download_json(HolderObject.UserData, "empty_file")

        gdrive_mock.download_file.assert_called_once()
