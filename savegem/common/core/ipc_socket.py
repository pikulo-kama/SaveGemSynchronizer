import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Final

from constants import UTF_8
from savegem.common.core import app
from savegem.common.util.logger import get_logger


_logger = get_logger(__name__)


class IPCCommand:
    """
    Contains commands that are used
    for IPC communication of main app
    with processes.
    """

    RefreshUI: Final = "refresh_ui"
    GUIInitialized: Final = "gui_initialized"
    StateChanged: Final = "state_changed"


class IPCProp:
    """
    Contains IPC message properties.
    """

    Command: Final = "command"
    Event: Final = "event"


class IPCSocket:

    def __init__(self, port):
        self.__socket_info = ("127.0.0.1", port)

    def listen(self):
        _logger.info("Starting IPC socket on port %d.", self.__socket_info[1])

        sock = socket(AF_INET, SOCK_STREAM)

        if self.__is_socket_running():
            _logger.error("Socket already opened on %s.", self.__socket_info)
            exit(1)

        sock.bind(self.__socket_info)
        sock.listen()

        while True:
            connection, _ = sock.accept()
            message = connection.recv(4096)
            message = json.loads(message.decode(UTF_8))
            _logger.info("Received message - %s", message)

            command = message.pop(IPCProp.Command)

            if command == IPCCommand.StateChanged:
                app.state.reload()

            else:
                self._handle(command, message)

            connection.close()

    def send(self, message):

        if isinstance(message, str):
            message = {IPCProp.Command: message}

        with socket(AF_INET, SOCK_STREAM) as sock:

            try:
                sock.connect(self.__socket_info)
                sock.sendall(json.dumps(message).encode(UTF_8))

            except ConnectionRefusedError as error:
                _logger.error(error)

    def __is_socket_running(self):
        """
        Used to check if socket already running.
        """

        sock = socket(AF_INET, SOCK_STREAM)
        is_running = sock.connect_ex(self.__socket_info) == 0
        sock.close()

        return is_running

    def _handle(self, command: str, message: dict):
        raise NotImplementedError()
