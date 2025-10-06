import pytest

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout
from PyQt6.QtCore import QMutex
from pytest_mock import MockerFixture

from savegem.app.gui.constants import UIRefreshEvent
from savegem.app.gui.window import gui, GUI


@pytest.fixture(autouse=True)
def _setup(module_patch, qtbot, _mutex_mock, prop_mock, tr_mock, resolve_resource_mock,  # noqa
                        app_state_mock, _load_builders_mock, app_context, games_config):

    prop_mock.side_effect = lambda key: {
        "name": "SaveGem App",
        "windowWidth": 800,
        "windowHeight": 600,
        "minWindowWidth": 400,
        "minWindowHeight": 300,
    }.get(key, "MockValue")

    tr_mock.return_value = "Mock Window Title"
    resolve_resource_mock.return_value = "path/to/icon.ico"

    app_state_mock.width = 800
    app_state_mock.height = 600

    # Reset _gui global instance.
    module_patch("_gui", new=None)

    # Make sure that actual window is not being shown.
    module_patch("GUI.show")


@pytest.fixture
def _primary_screen_mock(mocker: MockerFixture, module_patch):
    primary_screen_mock = module_patch("QApplication.primaryScreen")
    size_mock = mocker.MagicMock()

    size_mock.width.return_value = 1920
    size_mock.height.return_value = 1080

    primary_screen_mock.return_value. \
        size.return_value = size_mock

    return primary_screen_mock


@pytest.fixture
def _first_builder(mocker: MockerFixture):
    builder = mocker.MagicMock()
    builder.events = [UIRefreshEvent.All]

    return builder


@pytest.fixture
def _second_builder(mocker: MockerFixture):
    builder = mocker.MagicMock()
    builder.events = [UIRefreshEvent.All, UIRefreshEvent.ActivityLogUpdate]

    return builder


@pytest.fixture
def _builders(_first_builder, _second_builder):
    return [_first_builder, _second_builder]


@pytest.fixture
def _load_builders_mock(module_patch, _builders):
    return module_patch("load_builders", return_value=_builders)


@pytest.fixture
def _mutex_mock(module_patch):
    return module_patch("QMutex")


@pytest.fixture
def _after_init_callback(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def _before_destroy_callback(mocker: MockerFixture):
    return mocker.Mock()


def test_gui_singleton():
    """
    Test the gui() function ensures a singleton instance.
    """

    instance1 = gui()
    instance2 = gui()

    assert isinstance(instance1, GUI)
    assert instance1 is instance2


def test_gui_initialization(qtbot, prop_mock, tr_mock, resolve_resource_mock, _load_builders_mock,
                            _primary_screen_mock):
    """
    Test the GUI constructor initializes components and properties.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)

    # Check central widget and layout structure
    assert isinstance(app_gui.centralWidget(), QWidget)
    root_layout = app_gui.centralWidget().layout()
    assert isinstance(root_layout, QHBoxLayout)

    # Check window title and icon setting
    prop_mock.assert_any_call("name")
    tr_mock.assert_called_with("window_Title", "SaveGem App")
    assert app_gui.windowTitle() == "Translated(window_Title)"
    resolve_resource_mock.assert_called_once()

    # Check builder loading
    _load_builders_mock.assert_called_once()

    # Check centering logic
    # Screen (1920x1080), app_state (800x600) -> x=560, y=240
    assert app_gui.pos().x() == 560
    assert app_gui.pos().y() == 240
    assert app_gui.size().width() == 800
    assert app_gui.size().height() == 600

    # Check minimum size
    assert app_gui.minimumWidth() == 400
    assert app_gui.minimumHeight() == 300


def test_area_properties(qtbot):
    """
    Test that the property getters return the correct widgets.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)

    assert isinstance(app_gui.top_left, QWidget)
    assert isinstance(app_gui.top, QWidget)
    assert isinstance(app_gui.top_right, QWidget)
    assert isinstance(app_gui.center, QWidget)
    assert isinstance(app_gui.bottom_left, QWidget)
    assert isinstance(app_gui.bottom, QWidget)
    assert isinstance(app_gui.bottom_right, QWidget)


def test_gui_build_and_show(mocker: MockerFixture, qtbot, tr_mock, _builders):
    """
    Test the build method correctly configures the UI and calls builders.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)

    after_init_callback = mocker.Mock()
    app_gui.after_init.connect(after_init_callback)
    app_gui.build()

    # 1. Check if builders were linked and built
    for builder in _builders:
        builder.link.assert_called_with(app_gui)
        builder.build.assert_called_once()

    # 2. Check if refresh was called (implicitly by checking title update)
    # Since refresh calls 'tr', check if it was called twice (init + build)
    assert tr_mock.call_count == 2

    # 3. Check if is_blocked was set to False
    assert app_gui.is_blocked is False
    for builder in _builders:
        builder.enable.assert_called_once()
        builder.disable.assert_not_called()

    # 4. Check show() was called (hard to test directly, but assume successful execution)

    # 5. Check after_init signal emitted
    after_init_callback.assert_called_once()

    # 6. Check the grid layout structure was applied (e.g., stretches)
    grid_layout = app_gui.centralWidget().findChild(QGridLayout)
    assert grid_layout is not None
    # Check a specific stretch value from the build method
    # self.__grid_layout.setRowStretch(1, 5)
    assert grid_layout.rowStretch(1) == 5
    # self.center.setMaximumWidth(round(prop("windowWidth") * 0.7))
    assert app_gui.center.maximumWidth() == round(800 * 0.7)


def test_gui_refresh_all(_first_builder, _second_builder, qtbot, tr_mock):
    """
    Test refresh method with the default 'All' event.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)
    app_gui.build()  # Initialize builders

    # Reset mocks to check calls *during* refresh
    _first_builder.refresh.reset_mock()
    _second_builder.refresh.reset_mock()

    app_gui.refresh()

    # UIRefreshEvent.All is assumed to be in both builders' events
    _first_builder.refresh.assert_called_once()
    _second_builder.refresh.assert_called_once()

    # Check window title refresh
    # Called during init, build, and now refresh.
    assert tr_mock.call_count == 3


def test_gui_refresh_specific_event(qtbot, _first_builder, _second_builder):
    """
    Test refresh method with a specific event that only one builder handles.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)
    app_gui.build()  # Initialize builders

    _first_builder.refresh.reset_mock()
    _second_builder.refresh.reset_mock()

    app_gui.refresh(UIRefreshEvent.ActivityLogUpdate)

    # Builder 1 (with event 2) should be refreshed
    _first_builder.refresh.assert_not_called()
    # Builder 2 (without event 2) should NOT be refreshed
    _second_builder.refresh.assert_called_once()


def test_gui_is_blocked_setter_true(qtbot, _builders):
    """Test setting is_blocked to True disables builders."""
    app_gui = GUI()
    qtbot.addWidget(app_gui)
    app_gui.build()  # Ensure builders are initialized and enabled once

    # Reset mocks to check *new* calls
    for builder in _builders:
        builder.disable.reset_mock()
        builder.enable.reset_mock()

    app_gui.is_blocked = True

    assert app_gui.is_blocked is True
    for builder in _builders:
        builder.disable.assert_called_once()
        builder.enable.assert_not_called()


def test_gui_is_blocked_setter_false(qtbot, _builders):
    """Test setting is_blocked to False enables builders."""
    app_gui = GUI()
    qtbot.addWidget(app_gui)
    app_gui.build()
    app_gui.is_blocked = True  # Block it first

    # Reset mocks to check *new* calls
    for builder in _builders:
        builder.disable.reset_mock()
        builder.enable.reset_mock()

    app_gui.is_blocked = False

    assert app_gui.is_blocked is False
    for builder in _builders:
        builder.enable.assert_called_once()
        builder.disable.assert_not_called()


def test_gui_close_event(mocker: MockerFixture, qtbot, app_state_mock):
    """Test closeEvent updates app state and emits signal."""
    app_gui = GUI()
    qtbot.addWidget(app_gui)

    # Set up a fake size for the window
    app_gui.resize(999, 777)

    before_destroy_callback = mocker.Mock()
    app_gui.before_destroy.connect(before_destroy_callback)

    app_gui.closeEvent(QCloseEvent())

    # Check if app.state was updated with the new size
    assert app_state_mock.width == 999
    assert app_state_mock.height == 777

    # Check if before_destroy signal was emitted
    before_destroy_callback.assert_called_once()


def test_gui_mutex_initialization(qtbot):
    """
    Test that the mutex is correctly initialized.
    """

    app_gui = GUI()
    qtbot.addWidget(app_gui)

    assert isinstance(app_gui.mutex, QMutex)
