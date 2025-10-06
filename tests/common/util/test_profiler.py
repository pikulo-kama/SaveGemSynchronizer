import logging
from unittest import mock

import pytest

from savegem.common.util.profiler import measure_time


@measure_time()
def dummy_function_to_time(a, b=1):
    return a + b


@measure_time(when=logging.INFO)
def info_level_function():
    return True


@pytest.fixture
def _logger(module_patch):
    """Mocks the logger returned by get_logger."""
    # We mock the return value of get_logger
    mock_log = mock.Mock(spec=logging.Logger)
    module_patch("get_logger", return_value=mock_log)
    return mock_log


@pytest.fixture
def _time(module_patch):
    """Mocks time.time() to control elapsed time."""
    mock_time = module_patch("time.time")
    # Set the mock to return different values on sequential calls
    mock_time.side_effect = [100.0, 105.0]  # Start at 100.0, end at 105.0 (5 seconds elapsed)
    return mock_time


def test_measure_time_logs_elapsed_time(_logger, _time):
    """
    Tests that the logger is called with the correct time difference
    when the log level is enabled.
    """
    # 1. Configure logger to be enabled for DEBUG
    _logger.isEnabledFor.return_value = True

    # 2. Execute the decorated function
    result = dummy_function_to_time(5)

    # 3. Assertions
    assert result == 6
    _logger.isEnabledFor.assert_called_once_with(logging.DEBUG)

    # Time should be called twice (start and end)
    assert _time.call_count == 2

    # Expected log message: execution took 5.00 seconds (105.0 - 100.0)
    expected_message = f"{__name__}:dummy_function_to_time took 5.00 seconds"

    # Log function should be called with level=DEBUG, and the formatted message
    _logger.log.assert_called_once_with(logging.DEBUG, expected_message)


def test_measure_time_skips_when_level_is_disabled(_logger, _time):
    """
    Tests that time measurement is skipped if the logger is disabled for the level.
    """
    # 1. Configure logger to be disabled for DEBUG
    _logger.isEnabledFor.return_value = False

    # 2. Execute the decorated function
    result = dummy_function_to_time(10)

    # 3. Assertions
    assert result == 11
    _logger.isEnabledFor.assert_called_once_with(logging.DEBUG)

    # time.time() and logger.log() should NOT be called
    _time.assert_not_called()
    _logger.log.assert_not_called()


def test_measure_time_respects_custom_level(_logger):
    """
    Tests that the decorator uses the level passed in its argument (e.g., logging.INFO).
    """
    # 1. Configure logger
    _logger.isEnabledFor.return_value = True

    # We don't need to mock time.time() as we only check the level call

    # 2. Execute INFO level decorated function
    info_level_function()

    # 3. Assertions
    _logger.isEnabledFor.assert_called_once_with(logging.INFO)
    _logger.log.assert_called_once()

