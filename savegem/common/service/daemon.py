import abc
import os.path
import time
from typing import Final

from constants import JSON_EXTENSION
from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.util.file import resolve_config
from savegem.common.util.logger import get_logger


class Daemon(abc.ABC):
    """
    Wrapper for background service that is being executed
    with certain interval.
    """

    __DEFAULT_POLLING_RATE: Final = 60

    def __init__(self, service_name: str):

        self._logger = get_logger(service_name)
        self.__interval = self.__DEFAULT_POLLING_RATE
        self.__service_name = service_name
        config_path = resolve_config(service_name + JSON_EXTENSION)

        if os.path.exists(config_path):
            config = JsonConfigHolder(config_path)

            self._initialize(config)
            self.__interval = config.get_value("iterationIntervalSeconds", self.__DEFAULT_POLLING_RATE)

    def start(self):
        """
        Used to start daemon.
        """

        self._logger.info("Started daemon '%s' with interval %d second(s).", self.__service_name, self.__interval)

        while True:
            try:
                self._work()
            except Exception as error:  # noqa: E722
                self._logger.error("Exception in watcher service", error)

            time.sleep(self.__interval)

    @property
    def interval(self):
        """
        Sleep interval of daemon in seconds.
        """
        return self.__interval

    @abc.abstractmethod
    def _work(self):
        """
        Should have main logic of daemon.
        This method will run in between intervals.
        """
        pass

    def _initialize(self, config: JsonConfigHolder):
        """
        Should be used to initialize additional configurations.
        """
        pass
