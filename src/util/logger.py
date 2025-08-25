import logging

from constants import LOG_FILE_NAME
from src.core.JsonConfigHolder import JsonConfigHolder
from src.util.file import resolve_log, resolve_config


log_levels = JsonConfigHolder(resolve_config('logback.json'))
log_level_map = {
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "FATAL": logging.FATAL
}


def initialize_logging():
    logging.basicConfig(
        filename=resolve_log(LOG_FILE_NAME),
        encoding='utf-8',
        format='%(asctime)s - (%(name)s:%(lineno)d) [%(levelname)s] : %(message)s'
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
