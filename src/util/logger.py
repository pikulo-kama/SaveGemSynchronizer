import logging
import os.path
import re
from logging.handlers import TimedRotatingFileHandler

from constants import LOG_FILE_NAME, LOGBACK_FILE_NAME
from src.core.editable_json_config_holder import EditableJsonConfigHolder
from src.core.json_config_holder import JsonConfigHolder
from src.util.file import resolve_log, resolve_config, resolve_app_data


local_logback_file_path = resolve_config(LOGBACK_FILE_NAME)
app_data_logback_file_path = resolve_app_data(LOGBACK_FILE_NAME)

# Copy logback.json to app data if it's missing.
if not os.path.exists(app_data_logback_file_path):
    local_logback = JsonConfigHolder(local_logback_file_path)
    logback = EditableJsonConfigHolder(app_data_logback_file_path)
    logback.set(local_logback.get())

logback = JsonConfigHolder(app_data_logback_file_path)
log_levels = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL
}


def initialize_logging():
    """
    Used to initialize logging module.
    """

    handler = TimedRotatingFileHandler(
        resolve_log(LOG_FILE_NAME),
        when="midnight",
        interval=1,
        backupCount=5,
        encoding="utf-8"
    )

    handler.suffix = "%Y-%m-%d.log"
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")

    logging.basicConfig(
        encoding="utf-8",
        format="%(asctime)s - (%(name)s:%(lineno)d) [%(levelname)s] : %(message)s",
        handlers=[handler]
    )


def get_log_level(logger_name: str):
    """
    Used to query logback.xml and get configured log level for provided log name.
    If log level is not configured 'INFO' would be used as default.
    """

    level = logback.get_value(logger_name)

    if level is not None:
        return log_levels[level]

    return logging.INFO


def get_logger(logger_name: str):
    """
    Used to create logger for provided logger name.
    """

    logger = logging.getLogger(logger_name)
    level = get_log_level(logger_name)
    logger.setLevel(level)

    return logger
