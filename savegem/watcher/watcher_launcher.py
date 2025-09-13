import subprocess
import time


def _main():
    """
    Simple watchdog for process watcher EXE.
    """

    while True:
        process = subprocess.Popen(["ProcessWatcher.exe"])
        process.wait()
        time.sleep(30)


if __name__ == "__main__":
    _main()
