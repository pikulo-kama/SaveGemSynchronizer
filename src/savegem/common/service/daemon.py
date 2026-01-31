import abc
import os.path
import sys
import time
from typing import Final

from kui.core.json_holder import JsonConfigHolder
from kui.core.shortcut import prop, resolve_project_file
from kutil.file_type import JSON
from kutil.logger import get_logger
from kutil.process import is_process_already_running

from src.savegem.common.service.gdrive import GoogleAuth
from src.savegem.common.util.test import ExitTestLoop


class Daemon(abc.ABC):
    """
    Wrapper for background service that is being executed
    with certain interval.
    """

    DefaultInterval: Final = 5

    def __init__(self, service_name: str, requires_auth: bool):
        self._logger = get_logger(service_name)
        self.__interval = self.DefaultInterval
        self.__service_name = service_name
        self.__requires_auth = requires_auth
        config_path = resolve_project_file("serviceInfo", JSON.add_extension(service_name))

        if os.path.exists(config_path):
            config = JsonConfigHolder(config_path)
            process_name = config.get_value("processName")
            self.__interval = config.get_value("iterationIntervalSeconds", self.DefaultInterval)

            self._logger.debug("Process name for service %s = %s", self.__service_name, process_name)

            # If instance of process is already running then exit silently.
            if is_process_already_running(process_name):
                self._logger.error("Instance of %s is already running. Exiting.", process_name)
                sys.exit(0)

            self._initialize(config)

    def start(self):
        """
        Used to start daemon.
        """

        self._logger.info("Starting service '%s' version %s.", self.__service_name, prop("version"))
        self._logger.info("Polling rate '%s' seconds.", self.__interval)

        run_once_executed = False

        while True:
            try:
                # There are scenarios where we don't want to trigger authentication flow once user installs
                # application and background processes start.
                # Once user authenticates thorough UI it will create
                # token file, only then service can start doing their job.
                if self.__requires_auth and not GoogleAuth.is_authenticated():
                    self._logger.debug(
                        "Authentication has not been completed. Sleeping for %d second(s).",
                        self.interval
                    )
                    time.sleep(self.__interval)
                    continue

                if not run_once_executed:
                    self._logger.debug("First loop iteration reached. Executing 'run once' setup.")
                    self._run_once()
                    run_once_executed = True

                self._work()
            except ExitTestLoop as error:
                raise error

            except Exception as error:
                self._logger.error("Exception in '%s' service: %s", self.__service_name, error, exc_info=True)

            time.sleep(self.__interval)

    @property
    def interval(self):
        """
        Sleep interval of daemon in seconds.
        """
        return self.__interval

    @interval.setter
    def interval(self, interval: int):
        """
        Used to set interval in which
        daemon will run.
        """

        self.__interval = interval

    @abc.abstractmethod  # pragma: no cover
    def _work(self):
        """
        Should have main logic of daemon.
        This method will run in between intervals.
        """
        pass

    @abc.abstractmethod  # pragma: no cover
    def _run_once(self):
        """
        Allows to run one-time operations
        once daemon is operational.
        """
        pass

    def _initialize(self, config: JsonConfigHolder):  # pragma: no cover
        """
        Should be used to initialize additional configurations.
        """
        pass
