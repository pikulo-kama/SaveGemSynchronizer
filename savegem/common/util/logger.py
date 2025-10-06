import logging
import os.path
import re
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from constants import UTF_8, JSON_EXTENSION
from savegem.common.util.file import resolve_log, remove_extension_from_path, read_file, resolve_logback


# Name of running service/EXE
_log_file_name = remove_extension_from_path(os.path.basename(sys.argv[0]))
_logback: Optional[dict] = None
_initialized: bool = False


OFF_LOG_LEVEL = "OFF"
LogLevels = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL,
    OFF_LOG_LEVEL: OFF_LOG_LEVEL
}


def get_logger(logger_name: str):
    """
    Used to create logger for provided logger name.
    """

    _initialize_logging()

    logger = logging.getLogger(logger_name)
    level = _get_log_level(logger_name)

    if level == OFF_LOG_LEVEL:
        logger.disabled = True

    else:
        logger.setLevel(level)

    return logger


def _get_log_level(logger_name: str):
    """
    Used to query logback and get configured log level for provided log name.
    If log level is not configured 'INFO' would be used as default.
    """

    level = _get_logback(_log_file_name).get(logger_name)

    if level is not None:
        return LogLevels[level]

    return logging.INFO


def _get_logback(log_file_name: str):
    """
    Used to read logging configuration file.
    Will use running process name to get
    corresponding logging config.

    If it doesn't exist then default logback
    file would be used - logback/SaveGem.json
    """

    global _logback

    if _logback is None:
        logback_file_name = log_file_name + JSON_EXTENSION

        if not os.path.exists(resolve_logback(logback_file_name)):
            logback_file_name = "SaveGem" + JSON_EXTENSION

        _logback = read_file(resolve_logback(logback_file_name), as_json=True)

    return _logback


def _initialize_logging():
    """
    Used to initialize logging.
    Should be executed only once.
    """

    global _initialized

    if _initialized:
        return

    _handler = TimedRotatingFileHandler(
        resolve_log(f"{_log_file_name}.log"),
        when="midnight",
        interval=1,
        backupCount=5,
        encoding=UTF_8
    )

    _handler.suffix = "%Y-%m-%d.log"
    _handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s - (%(name)s:%(lineno)d) [%(levelname)s] : %(message)s"
    ))

    # Configure the root logger
    logging.getLogger().addHandler(_handler)
    _initialized = True
