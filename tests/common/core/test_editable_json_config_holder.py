import os

import pytest
from pytest_mock import MockerFixture

from savegem.common.core.editable_json_config_holder import EditableJsonConfigHolder
from savegem.common.util.file import save_file


@pytest.fixture(autouse=True)
def _setup(path_exists_mock):
    path_exists_mock.return_value = True


@pytest.fixture
def _test_config_path(tmp_path):
    return str(tmp_path / "test_config.json")


def test_initialization_ensures_file_exists(save_file_mock, _test_config_path):
    """
    Test that the file existence check and creation logic is triggered on initialization.
    """

    save_file(_test_config_path, {}, as_json=True)

    EditableJsonConfigHolder(_test_config_path)
    save_file_mock.assert_not_called()


def test_set_value_updates_data_and_saves(save_file_mock, _test_config_path):
    """
    Test that set_value updates the internal data and calls save_file.
    """

    save_file(_test_config_path, {}, as_json=True)

    # Initialize with some data (Note: JsonConfigHolder reads on init)
    # We mock out the reading by initializing _data directly for simplicity in this unit test
    holder = EditableJsonConfigHolder(_test_config_path)
    holder._data = {"old_key": 100}

    # 1. Call set_value
    holder.set_value("new_key", "test_value")

    # 2. Assert internal data is updated
    assert holder.get_value("new_key") == "test_value"
    assert holder.get_value("old_key") == 100  # Should retain old data

    # 3. Assert save_file was called exactly once
    save_file_mock.assert_called_once()

    # 4. Assert save_file was called with the correct path, data, and as_json=True
    expected_data = {"old_key": 100, "new_key": "test_value"}
    save_file_mock.assert_called_with(_test_config_path, expected_data, as_json=True)


def test_set_fully_replaces_data_and_saves(save_file_mock, _test_config_path):
    """
    Test that set fully replaces the internal data and calls save_file.
    """

    save_file(_test_config_path, {}, as_json=True)

    holder = EditableJsonConfigHolder(_test_config_path)
    holder._data = {"original_key": "original_value"}

    new_config = {"replacement_key": 42, "another_key": True}

    # 1. Call set
    holder.set(new_config)

    # 2. Assert internal data is fully replaced
    assert holder.get_value("replacement_key") == 42
    assert holder.get_value("original_key") is None  # Old key should be gone
    assert holder._data == new_config  # Check full replacement

    # 3. Assert save_file was called exactly once
    save_file_mock.assert_called_once()

    # 4. Assert save_file was called with the new data
    save_file_mock.assert_called_with(_test_config_path, new_config, as_json=True)


def test_before_file_open_creates_directories_and_default_file(mocker: MockerFixture, _test_config_path, save_file_mock,
                                                               makedirs_mock, path_exists_mock):
    """
    Test the _before_file_open logic when the config file does not exist.
    We must use a manual patch approach here to control os.path.exists behavior
    within this specific test.
    """

    mocker.patch.object(EditableJsonConfigHolder, "_load_data")

    # 2. Configure os.path.exists to return False (file does not exist)
    # We must patch it where it is used (os.path.exists is an alias for os.path.exists in the module)
    path_exists_mock.return_value = False

    # 3. Instantiate the holder (this will trigger _load() -> _before_file_open())
    EditableJsonConfigHolder(_test_config_path)

    # 4. Assert os.makedirs was called for the directory path
    expected_dir = os.path.dirname(_test_config_path)
    makedirs_mock.assert_called_once_with(expected_dir, exist_ok=True)

    # 5. Assert save_file was called to create the empty default file
    # This happens because os.path.exists returned False
    save_file_mock.assert_called_once_with(_test_config_path, {}, as_json=True)

    # 6. Sanity check: Assert mock_exists was called
    path_exists_mock.assert_called()
