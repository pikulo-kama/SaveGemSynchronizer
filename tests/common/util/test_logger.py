import logging
import pytest


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
