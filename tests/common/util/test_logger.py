import logging

import pytest
from pytest_mock import MockerFixture


# Disable logger mock
@pytest.fixture
def global_logger_mock():
    pass


@pytest.fixture
def logger_mock():
    pass


@pytest.fixture(scope="module", autouse=True)
def _setup_module():
    """
    Patches external dependencies (constants, file util) and system arguments
    before the module is imported to correctly set initial globals.
    """

    import savegem.common.util.logger as module
    module._log_file_name = "my_service"

    return module


@pytest.fixture
def _logging_mock(module_patch):
    return module_patch("logging")


@pytest.fixture
def _file_handler_mock(module_patch):
    return module_patch("TimedRotatingFileHandler")


@pytest.fixture
def _logger_module(_setup_module):
    """
    Resets the module's global state (_logback, _initialized) and root logger
    handlers before each test for isolation.
    """

    module = _setup_module

    # Reset module globals
    module._logback = None
    module._initialized = False

    # Clear handlers from the root logger for consistent testing of _initialize_logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    yield module


def test_get_logback_fallback_to_savegem(_logger_module, read_file_mock, path_exists_mock, resolve_logback_mock):
    """
    Tests falling back to 'SaveGem.json' if the specific file doesn't exist.
    """

    # Setup
    mock_logback_content = {"com.app": "INFO"}
    read_file_mock.return_value = mock_logback_content
    resolve_logback_mock.side_effect = lambda name: name

    # Mock os.path.exists: False for specific file, True for default ('SaveGem.json')
    path_exists_mock.side_effect = [False, True]

    # Execution
    logback = _logger_module._get_logback(_logger_module._log_file_name)

    # Assertions
    assert logback == mock_logback_content
    # Check that read_file was called with the fallback file name
    read_file_mock.assert_called_once_with(
        "SaveGem.json",
        as_json=True
    )


def test_get_logback_caching(_logger_module, read_file_mock):
    """
    Tests that logback is only read from the file system once.
    """

    read_file_mock.return_value = {"ROOT": "INFO"}

    _logger_module._get_logback('app')
    _logger_module._get_logback('app')

    read_file_mock.assert_called_once()


@pytest.mark.parametrize("log_name, configured_level, expected_level", [
    ("com.app.worker", "DEBUG", logging.DEBUG),
    ("com.app.api", "WARN", logging.WARN),
    ("com.app.disabled", "OFF", "OFF"),
])
def test_get_log_level_configured(mocker: MockerFixture, _logger_module, log_name, configured_level, expected_level):
    """
    Tests getting a log level configured in logback.
    """

    # Mock _get_logback to return a configuration including the test level
    mock_logback = {log_name: configured_level, "ROOT": "INFO"}
    mocker.patch.object(_logger_module, '_get_logback', return_value=mock_logback)

    level = _logger_module._get_log_level(log_name)

    assert level == expected_level


def test_get_log_level_default(_logger_module, mocker):
    """
    Tests falling back to the default level (logging.INFO).
    """

    mocker.patch.object(_logger_module, '_get_logback', return_value={"com.other.app": "DEBUG"})

    level = _logger_module._get_log_level("un_configured.logger")

    assert level == logging.INFO


def test_initialize_logging_first_call(module_patch, _logger_module, _logging_mock, _file_handler_mock,
                                       resolve_log_mock):
    """
    Tests that logging is initialized correctly on the first call, setting up the root logger.
    """

    from constants import UTF_8

    module_patch("logging.Formatter")
    resolve_log_mock.side_effect = lambda name: name

    _logger_module._initialize_logging()

    # 1. Check TimedRotatingFileHandler creation
    _file_handler_mock.assert_called_once_with(
        "my_service.log",
        when="midnight",
        interval=1,
        backupCount=5,
        encoding=UTF_8
    )

    # 2. Check handler configuration (suffix and formatter)
    assert _file_handler_mock.return_value.suffix == "%Y-%m-%d.log"
    _file_handler_mock.return_value.setFormatter.assert_called()

    _logging_mock.getLogger.return_value.addHandler.assert_called_with(_file_handler_mock.return_value)

    # 4. Check global state update
    assert _logger_module._initialized is True


def test_initialize_logging_second_call_ignored(module_patch, _file_handler_mock, _logger_module):
    """
    Tests that logging initialization is skipped after the first time.
    """

    # First, manually set _initialized=True
    _logger_module._initialized = True

    # Execute again
    _logger_module._initialize_logging()

    # Assertions: Should not call the handler constructor
    _file_handler_mock.assert_not_called()


def test_get_logger_initializes_logging(module_patch, _logger_module, mocker):
    """
    Tests that get_logger calls _initialize_logging.
    """

    initialize_logging_mock = module_patch('_initialize_logging')

    # Mock dependencies to avoid full setup
    mocker.patch.object(_logger_module, "_get_log_level", return_value=logging.INFO)

    _logger_module.get_logger("test_logger")

    initialize_logging_mock.assert_called_once()


def test_get_logger_level_configured(_logger_module, mocker, _logging_mock):
    """
    Tests logger returned with a specific, non-OFF log level.
    """

    mock_logger = _logging_mock.getLogger.return_value
    mock_logger.disabled = False

    mocker.patch.object(_logger_module, "_initialize_logging")
    mocker.patch.object(_logger_module, "_get_log_level", return_value=logging.DEBUG)

    logger = _logger_module.get_logger("test_logger_debug")

    assert logger is mock_logger
    _logging_mock.getLogger.assert_called_with("test_logger_debug")
    mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
    assert mock_logger.disabled is False


def test_get_logger_level_off(_logging_mock, _logger_module, mocker):
    """
    Tests logger returned with 'OFF' level is disabled.
    """

    mocker.patch.object(_logger_module, '_initialize_logging')
    mocker.patch.object(_logger_module, '_get_log_level', return_value=_logger_module.OFF_LOG_LEVEL)

    logger = _logger_module.get_logger("test_logger_off")
    get_logger_mock = _logging_mock.getLogger.return_value

    assert logger is get_logger_mock
    _logging_mock.getLogger.assert_called_with("test_logger_off")
    get_logger_mock.setLevel.assert_not_called()
    assert get_logger_mock.disabled is True
