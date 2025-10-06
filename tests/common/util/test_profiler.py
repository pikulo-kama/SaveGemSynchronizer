import logging

import pytest


@pytest.fixture
def _dummy_function_to_time():
    from savegem.common.util.profiler import measure_time

    @measure_time()
    def _function(a, b=1):
        return a + b

    return _function


@pytest.fixture
def _info_level_function():
    from savegem.common.util.profiler import measure_time

    @measure_time(when=logging.INFO)
    def _function():
        return True

    return _function


def test_measure_time_logs_elapsed_time(logger_mock, time_mock, _dummy_function_to_time):
    """
    Tests that the logger is called with the correct time difference
    when the log level is enabled.
    """

    # 1. Configure logger to be enabled for DEBUG
    logger_mock.isEnabledFor.return_value = True
    time_mock.side_effect = [100.0, 105.0]

    # 2. Execute the decorated function
    result = _dummy_function_to_time(5)

    # 3. Assertions
    assert result == 6
    logger_mock.isEnabledFor.assert_called_once_with(logging.DEBUG)

    # Time should be called twice (start and end)
    assert time_mock.call_count == 2

    # Expected log message: execution took 5.00 seconds (105.0 - 100.0)
    expected_message = f"{__name__}:_function took 5.00 seconds"

    # Log function should be called with level=DEBUG, and the formatted message
    logger_mock.log.assert_called_once_with(logging.DEBUG, expected_message)


def test_measure_time_skips_when_level_is_disabled(logger_mock, time_mock, _dummy_function_to_time):
    """
    Tests that time measurement is skipped if the logger is disabled for the level.
    """

    # 1. Configure logger to be disabled for DEBUG
    logger_mock.isEnabledFor.return_value = False
    time_mock.side_effect = [100.0, 105.0]

    # 2. Execute the decorated function
    result = _dummy_function_to_time(10)

    # 3. Assertions
    assert result == 11
    logger_mock.isEnabledFor.assert_called_once_with(logging.DEBUG)

    # time.time() and logger.log() should NOT be called
    time_mock.assert_not_called()
    logger_mock.log.assert_not_called()


def test_measure_time_respects_custom_level(logger_mock, _info_level_function):
    """
    Tests that the decorator uses the level passed in its argument (e.g., logging.INFO).
    """

    # 1. Configure logger
    logger_mock.isEnabledFor.return_value = True

    # We don't need to mock time.time() as we only check the level call

    # 2. Execute INFO level decorated function
    _info_level_function()

    # 3. Assertions
    logger_mock.isEnabledFor.assert_called_once_with(logging.INFO)
    logger_mock.log.assert_called_once()
