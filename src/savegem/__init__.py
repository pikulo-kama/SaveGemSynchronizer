import os
import sys

from kui.core.app import KamaApplication
from kui.core.shortcut import resolve_logback
from kutil import logger
from kutil.file import remove_extension_from_path
from kutil.file_type import JSON


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = exception_hook

_application = KamaApplication()
_executable_name = remove_extension_from_path(os.path.basename(sys.argv[0]))

logger.initialize_logging(
    log_target_directory=_application.discovery.Logs,
    logback_path=resolve_logback(JSON.add_extension(_executable_name))
)
