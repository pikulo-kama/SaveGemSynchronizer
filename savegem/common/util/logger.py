import logging
import os.path
import re
import sys
from logging.handlers import TimedRotatingFileHandler

from constants import File, UTF_8
from savegem.common.util.file import resolve_log, resolve_app_data, remove_extension_from_path, read_file

_logback = read_file(resolve_app_data(File.Logback), as_json=True)
LogLevels = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL
}

# Name of running service/EXE
_log_file_name = remove_extension_from_path(os.path.basename(sys.argv[0]))

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


def get_logger(logger_name: str):
    """
    Used to create logger for provided logger name.
    """

    logger = logging.getLogger(logger_name)
    level = _get_log_level(logger_name)
    logger.setLevel(level)

    return logger


def _get_log_level(logger_name: str):
    """
    Used to query logback.json and get configured log level for provided log name.
    If log level is not configured 'INFO' would be used as default.
    """

    level = _logback.get(logger_name)

    if level is not None:
        return LogLevels[level]

    return logging.INFO
