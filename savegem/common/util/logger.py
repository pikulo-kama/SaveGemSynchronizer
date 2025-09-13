import logging
import os.path
import re
import sys
from logging.handlers import TimedRotatingFileHandler

from constants import File
from savegem.common.util.file import resolve_log, resolve_app_data, remove_extension_from_path, read_file

_logback = read_file(resolve_app_data(File.Logback), as_json=True)
_log_levels = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL
}


def get_logger(logger_name: str):
    """
    Used to create logger for provided logger name.
    """

    logger = logging.getLogger(logger_name)
    level = _get_log_level(logger_name)
    logger.setLevel(level)
    log_file_name = remove_extension_from_path(os.path.basename(sys.argv[0]))

    handler = TimedRotatingFileHandler(
        resolve_log(f"{log_file_name}.log"),
        when="midnight",
        interval=1,
        backupCount=5,
        encoding="utf-8"
    )

    handler.suffix = "%Y-%m-%d.log"
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - (%(name)s:%(lineno)d) [%(levelname)s] : %(message)s"
    ))

    logger.addHandler(handler)
    return logger


def _get_log_level(logger_name: str):
    """
    Used to query logback.json and get configured log level for provided log name.
    If log level is not configured 'INFO' would be used as default.
    """

    level = _logback.get(logger_name)

    if level is not None:
        return _log_levels[level]

    return logging.INFO
