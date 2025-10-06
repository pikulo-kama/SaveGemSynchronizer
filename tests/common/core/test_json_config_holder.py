import pytest
from pytest_mock import MockerFixture

from constants import JSON_EXTENSION
from savegem.common.core.json_config_holder import JsonConfigHolder


MockData = {"key1": 123, "key2": "value"}


@pytest.fixture(autouse=True)
def _setup(read_file_mock):
    read_file_mock.return_value = MockData


def test_initialization_appends_extension_if_missing(read_file_mock):
    """
    Test that the JSON extension is automatically appended to the config_path
    if it's not present.
    """

    config_name = "test_config"
    expected_path = config_name + JSON_EXTENSION

    holder = JsonConfigHolder(config_name)

    # Assert that the internal path was set correctly
    assert holder._config_path == expected_path

    # Assert that read_file was called with the corrected path
    read_file_mock.assert_called_once_with(expected_path, as_json=True)


def test_initialization_uses_provided_path_if_extension_present(read_file_mock):
    """
    Test that the config_path is used as-is if the extension is already present.
    """

    expected_path = "test_config" + JSON_EXTENSION

    holder = JsonConfigHolder(expected_path)

    # Assert that the internal path was set correctly
    assert holder._config_path == expected_path

    # Assert that read_file was called with the exact path
    read_file_mock.assert_called_once_with(expected_path, as_json=True)


def test_initialization_calls_before_file_open_and_load_data(mocker: MockerFixture, read_file_mock):
    """
    Test the sequence of initialization calls.
    """

    mock_before_file_open = mocker.spy(JsonConfigHolder, '_before_file_open')

    holder = JsonConfigHolder("test_config")

    # 1. Assert _before_file_open was called
    mock_before_file_open.assert_called_once()

    # 2. Assert _load_data (via read_file) was called
    read_file_mock.assert_called_once()

    # 3. Assert internal data was loaded
    assert holder._data == MockData


def test_get_value_retrieves_existing_property():
    """
    Test that get_value retrieves data correctly.
    """

    holder = JsonConfigHolder("test_config")

    # Test for string value
    assert holder.get_value("key2") == "value"

    # Test for numeric value
    assert holder.get_value("key1") == 123


def test_get_value_returns_default_for_non_existing_property():
    """
    Test that get_value returns the default_value if the property is missing.
    """
    JsonConfigHolder("test_config")

    holder = JsonConfigHolder("test_config")

    # Test with custom default value
    assert holder.get_value("non_existent_key", default_value="NOT_FOUND") == "NOT_FOUND"

    # Test with default None (implicit default)
    assert holder.get_value("another_missing_key") is None


def test_get_returns_full_configuration_map():
    """
    Test that get returns the full internal data dictionary.
    """

    holder = JsonConfigHolder("test_config")

    full_config = holder.get()

    assert full_config == MockData
    # Ensure it returns a reference/copy of the loaded data
    assert isinstance(full_config, dict)


def test_load_data_updates_internal_data(read_file_mock):
    """
    Test _load_data explicitly reads the file and updates _data.
    """

    holder = JsonConfigHolder("test_config")

    # Change the mock return value for the second call
    new_mock_data = {"new_key": 456}
    read_file_mock.return_value = new_mock_data

    # Call _load_data explicitly
    holder._load_data()

    # Assert read_file was called a second time
    assert read_file_mock.call_count == 2

    # Assert internal data was updated
    assert holder.get() == new_mock_data
