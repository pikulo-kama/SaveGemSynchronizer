from savegem.common.core.json_config_holder import JsonConfigHolder
from savegem.common.service.daemon import Daemon
from savegem.common.util.test import ExitTestLoop

import subprocess
import threading
import time


class Watchdog(Daemon):
    """
    Process that is responsible for making sure
    that all registered processes are running.
    If for some reason one of the processes will die,
    watcher will restart it.
    """

    def __init__(self):
        Daemon.__init__(self, "watchdog", False)

    def _initialize(self, config: JsonConfigHolder):
        # Start thread for each process that needs to
        # be watched.
        for process_name in config.get_value("childProcesses"):
            thread = threading.Thread(target=self.__watch_process, args=(process_name,), daemon=True)
            self._logger.info("Registered process %s in watchdog.", process_name)

            thread.start()

    def _work(self):  # pragma: no cover
        # All processes would be watched
        # in separate threads, we just need to make
        # sure that main thread of watchdog is alive.
        pass

    def __watch_process(self, args):
        """
        Callback method executed
        for each process in separate thread.
        """

        while True:
            try:
                self._logger.info("Starting process with args %s", args)
                process = subprocess.Popen(args)
                process.wait()

                self._logger.error("Process with args %s exited. Restarting in %ds...", args, self.interval)

            except ExitTestLoop as error:
                raise error

            except Exception as error:
                self._logger.error("Error in watchdog: %s", error, exc_info=True)

            time.sleep(self.interval)


if __name__ == "__main__":  # pragma: no cover
    Watchdog().start()
