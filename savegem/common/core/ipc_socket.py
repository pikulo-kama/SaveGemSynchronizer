import json
from socket import socket, AF_INET, SOCK_STREAM
from typing import Final

from constants import UTF_8
from savegem.common.core.context import app
from savegem.common.util.logger import get_logger
from savegem.common.util.test import ExitTestLoop


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
    """
    Socket wrapper used to accept messages.
    """

    Localhost: Final = "127.0.0.1"
    MessageSize: Final = 4096

    def __init__(self, port):
        self.__socket_info = (self.Localhost, port)

    @property
    def port(self):
        """
        Used to get port on which socket is running.
        """
        return self.__socket_info[1]

    def listen(self):
        """
        Used to listen for incoming messages.
        """

        if self.__is_socket_running():
            _logger.error("Socket already opened on %s.", self.__socket_info)
            exit(1)

        _logger.info("Starting IPC socket on port %d.", self.__socket_info[1])

        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(self.__socket_info)
        sock.listen()

        while True:
            try:
                connection, _ = sock.accept()
                message = connection.recv(self.MessageSize)
                message = json.loads(message.decode(UTF_8))
                _logger.info("Received message - %s", message)

                command = message.pop(IPCProp.Command)

                if command == IPCCommand.StateChanged:
                    app().state.refresh()

                else:
                    self._handle(command, message)

                connection.close()

            except ExitTestLoop as error:
                raise error

            except Exception as error:
                _logger.error("Error handling received message: %s", error, exc_info=True)

    def send(self, message):
        """
        Used to send message to the socket.
        Expects a dict object with "command" property.

        If string is provided as message it would be
        automatically treated as command name.
        """

        if isinstance(message, str):
            message = {IPCProp.Command: message}

        with socket(AF_INET, SOCK_STREAM) as sock:

            try:
                sock.connect(self.__socket_info)
                sock.sendall(json.dumps(message).encode(UTF_8))

            except ConnectionRefusedError as error:
                _logger.error(error, exc_info=True)

    def __is_socket_running(self):
        """
        Used to check if socket already running.
        """

        sock = socket(AF_INET, SOCK_STREAM)
        is_running = sock.connect_ex(self.__socket_info) == 0
        sock.close()

        return is_running

    def _handle(self, command: str, message: dict):  # pragma: no cover
        """
        Should be overridden by child classes.
        Used to handle socket implementation specific messages.
        """
        pass
