import logging
import pytest

from constants import JSON_EXTENSION
from savegem.common.util.logger import _get_logback, get_logger, OFF_LOG_LEVEL  # noqa


DEFAULT_LOGBACK_DATA = {"root": "INFO", "SaveGem": "DEBUG"}
CUSTOM_LOGBACK_DATA = {"app": "WARN", "CustomApp": "ERROR"}


@pytest.fixture(autouse=True)
def _setup(resolve_logback_mock, read_file_mock):
    resolve_logback_mock.side_effect = lambda name: f"/mock/path/{name}"
    read_file_mock.side_effect = lambda path, as_json: (
        CUSTOM_LOGBACK_DATA if "CustomApp" in path else DEFAULT_LOGBACK_DATA
    )


@pytest.fixture
def _logger_module():
    """
    Patches the global _log_levels in the module to ensure consistent mapping
    and prevents the module from initializing the logger on import.
    """

    import savegem.common.util.logger as logger_module
    yield logger_module


def test_returns_configured_level_when_present(_logger_module):
    """
    Tests that the correct mapped log level is returned when configured.
    """

    # Set the mock _logback dictionary
    _logger_module._logback = {
        "root": "INFO",
        "module_a": "DEBUG",
        "module_b": "ERROR"
    }

    # Test configured levels
    assert _logger_module._get_log_level("module_a") == logging.DEBUG
    assert _logger_module._get_log_level("module_b") == logging.ERROR
    assert _logger_module._get_log_level("root") == logging.INFO


def test_returns_info_default_when_not_configured(_logger_module):
    """
    Tests that logging.INFO is returned for not configured logger.
    """

    # Set the mock _logback dictionary
    _logger_module._logback = {
        "known_module": "WARN"
    }

    # Test not configured level
    assert _logger_module._get_log_level("unknown_module") == logging.INFO
    assert _logger_module._get_log_level("another_unknown") == logging.INFO


def test_raises_key_error_for_invalid_level_string(_logger_module):
    """
    Tests that a KeyError is raised if the configuration contains an invalid log level string.
    """

    # Set the mock _logback dictionary with an invalid level
    _logger_module._logback = {
        "bad_module": "CRITICAL"  # Assuming CRITICAL is NOT in the MOCK_LOG_LEVELS
    }

    # The method should raise KeyError when trying to access MOCK_LOG_LEVELS["CRITICAL"]
    with pytest.raises(KeyError):
        _logger_module._get_log_level("bad_module")


def test_handles_empty_logback(_logger_module):
    """
    Tests that it defaults to INFO when _logback is empty.
    """

    module = _logger_module
    module._logback = {}
    assert module._get_log_level("any_module") == logging.INFO


def test_get_logback_uses_default_when_custom_config_missing(path_exists_mock, resolve_logback_mock, read_file_mock):
    """
    Test that if the log file name's config does not exist,
    it falls back to 'SaveGem.json'.
    """

    # Setup: Ensure the custom file is reported as NOT existing
    path_exists_mock.return_value = False

    log_file_name = "MyService"

    # ACT
    result = _get_logback(log_file_name)

    # ASSERT
    # 1. Check if os.path.exists was called for the custom file name
    path_exists_mock.assert_called_with(resolve_logback_mock(log_file_name + JSON_EXTENSION))

    # 2. Check that read_file was called with the DEFAULT logback file name
    expected_path = f"/mock/path/SaveGem{JSON_EXTENSION}"
    read_file_mock.assert_called_once_with(expected_path, as_json=True)

    # 3. Check the returned data is the default data
    assert result == DEFAULT_LOGBACK_DATA


def test_get_logback_uses_custom_config_when_present(path_exists_mock, resolve_logback_mock, read_file_mock):
    """
    Test that if the log file name's config exists, it is used.
    """

    # Setup: Configure os.path.exists to return TRUE for the custom file
    path_exists_mock.return_value = True

    log_file_name = "CustomApp"

    # ACT
    result = _get_logback(log_file_name)

    # ASSERT
    # 1. Check if os.path.exists was called for the custom file name
    path_exists_mock.assert_called_with(resolve_logback_mock(log_file_name + JSON_EXTENSION))

    # 2. Check that read_file was called with the CUSTOM logback file name
    expected_path = f"/mock/path/CustomApp{JSON_EXTENSION}"
    read_file_mock.assert_called_once_with(expected_path, as_json=True)

    # 3. Check the returned data is the custom data
    assert result == CUSTOM_LOGBACK_DATA


def test_get_logger_sets_disabled_to_true_when_level_is_off(_logger_module):
    """
    Verifies that if the logback config specifies 'OFF', the logger's
    'disabled' attribute is set to True.
    """

    logger_name = "test_logger_off"
    _logger_module._logback = {
        logger_name: OFF_LOG_LEVEL
    }

    # ACT
    # This calls _get_log_level, which reads from the mocked _logback
    logger = get_logger(logger_name)

    # ASSERT
    # 1. Check the logger instance is correctly disabled
    assert logger.disabled is True

    # 2. Check the logger level (should still be NOTSET if disabled=True)
    # The setLevel line is skipped, so the level should be NOTSET (0)
    assert logger.level == logging.NOTSET
