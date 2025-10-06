import pytest
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from pytest_mock import MockerFixture


@pytest.fixture
def qt_app_mock(module_patch):
    return module_patch("QApplication")


@pytest.fixture
def gui_mock(mocker: MockerFixture, safe_patch, safe_module_patch):

    mock = mocker.MagicMock()

    safe_module_patch("gui", return_value=mock)
    safe_patch("savegem.app.gui.window.gui", return_value=mock)

    return mock


@pytest.fixture
def simple_gui(mocker: MockerFixture, qtbot, safe_patch, safe_module_patch):

    gui = QWidget()
    top_left = QWidget()
    top = QWidget()
    top_right = QWidget()
    center = QWidget()

    top_left.setLayout(QGridLayout())
    top.setLayout(QVBoxLayout())
    top_right.setLayout(QGridLayout())
    center.setLayout(QGridLayout())

    # Spy on layout methods.
    for widget in [top_left, top, top_right, center]:
        mocker.spy(widget.layout(), "addWidget")
        mocker.spy(widget.layout(), "setContentsMargins")

    gui.top_left = top_left
    gui.top = top
    gui.top_right = top_right
    gui.center = center

    qtbot.addWidget(gui)
    qtbot.addWidget(top_left)
    qtbot.addWidget(top)
    qtbot.addWidget(top_right)
    qtbot.addWidget(center)

    gui.refresh = mocker.Mock()
    mocker.spy(gui, "destroy")

    safe_module_patch("gui", return_value=gui)
    safe_patch("savegem.app.gui.window.gui", return_value=gui)

    return gui


@pytest.fixture
def qthread_mock(module_patch):
    return module_patch("QThread", spec=QThread)


@pytest.fixture
def exec_block_thread_mock(module_patch):
    return module_patch("execute_in_blocking_thread")


@pytest.fixture
def push_notification_mock(module_patch):
    return module_patch("push_notification")


@pytest.fixture
def notification_mock(module_patch):
    return module_patch("notification")


@pytest.fixture
def confirmation_mock(module_patch):
    return module_patch("confirmation")
