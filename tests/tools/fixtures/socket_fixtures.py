import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def ipc_socket_base_mock(module_patch):
    return module_patch("IPCSocket")


@pytest.fixture
def ipc_socket_base_init_mock(module_patch):
    return module_patch("IPCSocket.__init__")


@pytest.fixture
def ui_socket_mock(module_patch):
    return module_patch("ui_socket")


@pytest.fixture
def gdrive_watcher_socket_mock(mocker: MockerFixture, module_patch):
    socket_mock = mocker.MagicMock()
    module_patch("google_drive_watcher_socket", socket_mock)

    return socket_mock


@pytest.fixture
def process_watcher_socket_mock(mocker: MockerFixture, module_patch):
    socket_mock = mocker.MagicMock()
    module_patch("process_watcher_socket", socket_mock)

    return socket_mock
