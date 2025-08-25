import logging
import os.path
import re
from logging.handlers import TimedRotatingFileHandler

from constants import LOG_FILE_NAME, LOGBACK_FILE_NAME
from src.core.EditableJsonConfigHolder import EditableJsonConfigHolder
from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_log, resolve_config, resolve_app_data


local_logback_file_name = resolve_config(LOGBACK_FILE_NAME)
app_data_logback_file_name = resolve_app_data(LOGBACK_FILE_NAME)

# Copy logback.json to app data if it's missing.
if not os.path.exists(app_data_logback_file_name):
    local_log_levels = JsonConfigHolder(local_logback_file_name)
    log_levels = EditableJsonConfigHolder(app_data_logback_file_name)
    log_levels.set(local_log_levels.get())

log_levels = JsonConfigHolder(app_data_logback_file_name)
log_level_map = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL
}


def initialize_logging():

    handler = TimedRotatingFileHandler(
        resolve_log(LOG_FILE_NAME),
        when="midnight",
        interval=1,
        backupCount=5,
        encoding='utf-8'
    )

    handler.suffix = "%Y-%m-%d.log"
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")

    logging.basicConfig(
        encoding='utf-8',
        format='%(asctime)s - (%(name)s:%(lineno)d) [%(levelname)s] : %(message)s',
        handlers=[handler]
    )


def log_level(logger_name: str):
    level = log_levels.get_value(logger_name)

    if level is not None:
        return log_level_map[level]

    return logging.INFO


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level(logger_name))

    return logger
