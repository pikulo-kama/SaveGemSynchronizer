import pytest
import json
from pytest_mock import MockerFixture

from constants import UTF_8
from savegem.common.core import ApplicationContext
from savegem.common.core.ipc_socket import IPCSocket, IPCProp, IPCCommand
from tests.test_data import SocketTestData


@pytest.fixture
def _app_state(mocker: MockerFixture):
    mock_state = mocker.MagicMock()
    mocker.patch.object(ApplicationContext, 'state', new=mock_state)

    return mock_state


@pytest.fixture
def _socket(mocker: MockerFixture):
    return mocker.patch('savegem.common.core.ipc_socket.socket')


@pytest.fixture
def _ipc_socket():
    return IPCSocket(port=SocketTestData.UIPort)


def test_is_socket_running_true(_ipc_socket, _socket, logger_mock):
    mock_instance = _socket.return_value

    # Configure connect_ex to simulate success (return code 0)
    mock_instance.connect_ex.return_value = 0

    with pytest.raises(SystemExit):
        _ipc_socket.listen()

    mock_instance.connect_ex.assert_called_once_with((IPCSocket.Localhost, SocketTestData.UIPort))
    mock_instance.close.assert_called_once()
    logger_mock.error.assert_called_once()


def test_is_socket_running_false(_ipc_socket, _socket):
    mock_instance = _socket.return_value

    # Configure connect_ex to simulate failure (non-zero code)
    mock_instance.connect_ex.return_value = 1

    assert _ipc_socket._IPCSocket__is_socket_running() is False  # noqa
    mock_instance.connect_ex.assert_called_once()
    mock_instance.close.assert_called_once()


def test_listen_state_changed_command(mocker: MockerFixture, _ipc_socket, _socket, _app_state):
    test_message = {IPCProp.Command: IPCCommand.StateChanged}
    encoded_message = json.dumps(test_message).encode(UTF_8)

    # Mock the internal private check to ensure it returns False and doesn't exit
    mocker.patch.object(_ipc_socket, '_IPCSocket__is_socket_running', return_value=False)
    mock_handle = mocker.patch.object(_ipc_socket, '_handle')

    # Get mock instances of the socket objects
    mock_server_sock = _socket.return_value
    mock_connection = mocker.MagicMock()

    # Configure recv to return the message, and then raise an exception
    # to break the infinite loop after one successful message processing
    mock_connection.recv.side_effect = [
        encoded_message,
        Exception("Stop listening after one message")
    ]

    # Configure sock.accept() to return the connection mock
    mock_server_sock.accept.return_value = (mock_connection, (IPCSocket.Localhost, SocketTestData.ProcessWatcherPort))

    with pytest.raises(Exception, match="Stop listening after one message"):
        _ipc_socket.listen()

    # Verify the IPC socket setup
    mock_server_sock.bind.assert_called_once_with((IPCSocket.Localhost, SocketTestData.UIPort))
    mock_server_sock.listen.assert_called_once()

    # Verify the message was processed
    mock_connection.recv.assert_called_with(IPCSocket.MessageSize)
    mock_connection.close.call_count = 2
    mock_server_sock.accept.call_count = 2

    # Verify the core logic: app.state.refresh was called
    _app_state.refresh.assert_called_once()

    # Verify _handle was NOT called
    mock_handle.assert_not_called()


def test_listen_custom_command(mocker: MockerFixture, _ipc_socket, _socket, _app_state):
    mocker.patch.object(_ipc_socket, '_IPCSocket__is_socket_running', return_value=False)

    test_command = "custom_action"
    test_message = {IPCProp.Command: test_command, "payload": "data"}
    encoded_message = json.dumps(test_message).encode(UTF_8)

    # Mock the abstract _handle method
    mock_handle = mocker.patch.object(_ipc_socket, '_handle')

    socket_mock = _socket.return_value
    mock_connection = mocker.MagicMock()

    mock_connection.recv.side_effect = [encoded_message, Exception("Stop listening")]
    socket_mock.accept.return_value = (mock_connection, (IPCSocket.Localhost, SocketTestData.ProcessWatcherPort))

    with pytest.raises(Exception, match="Stop listening"):
        _ipc_socket.listen()

    mock_handle.assert_called_once_with(test_command, {"payload": "data"})
    _app_state.refresh.assert_not_called()


def test_send_string_command_success(_ipc_socket, _socket):
    socket_mock = _socket.return_value
    socket_mock.__enter__.return_value = socket_mock

    _ipc_socket.send(IPCCommand.RefreshUI)

    expected_message = json.dumps({IPCProp.Command: IPCCommand.RefreshUI}).encode(UTF_8)
    socket_mock.sendall.assert_called_once_with(expected_message)
    socket_mock.connect.assert_called_once_with((IPCSocket.Localhost, SocketTestData.UIPort))
    socket_mock.__exit__.assert_called_once()


def test_send_dict_message_success(_ipc_socket, _socket):
    test_message = {IPCProp.Command: "test", "data": [1, 2]}

    mock_instance = _socket.return_value
    mock_instance.__enter__.return_value = mock_instance

    _ipc_socket.send(test_message)

    expected_message = json.dumps(test_message).encode(UTF_8)
    mock_instance.sendall.assert_called_once_with(expected_message)


def test_send_connection_refused_error(_ipc_socket, _socket, logger_mock):
    error = ConnectionRefusedError()

    mock_instance = _socket.return_value
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.connect.side_effect = error

    _ipc_socket.send("test_command")

    logger_mock.error.assert_called_once_with(error)


def test_should_throw_not_implemented_in_handle(_ipc_socket):
    with pytest.raises(NotImplementedError):
        _ipc_socket._handle("", {})
