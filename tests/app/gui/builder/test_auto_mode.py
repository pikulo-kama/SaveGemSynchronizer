import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture

from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.builder.auto_mode import AutoModeBuilder
from savegem.app.gui.constants import QAttr, QKind, QObjectName


@pytest.fixture(autouse=True)
def _setup(tr_mock, app_context, app_state_mock):
    app_state_mock.is_auto_mode = False  # Default initial state


@pytest.fixture
def _auto_mode_builder(simple_gui):
    """
    Provides a fully mocked and initialized AutoModeBuilder instance.
    """

    builder = AutoModeBuilder()
    builder._gui = simple_gui

    return builder


def test_auto_mode_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor correctly initializes the base class and internal attributes.
    """

    # Spy on the base class __init__
    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)

    # Act
    builder = AutoModeBuilder()

    # Assert
    mock_super_init.assert_called_once_with()
    assert builder._AutoModeBuilder__auto_mode_button is None  # noqa


def test_build_creates_button_and_registers_it(mocker: MockerFixture, _auto_mode_builder, simple_gui):
    """
    Test build() creates the button, connects the callback, and adds it to the layout.
    """

    mock_add_interactable = mocker.patch.object(_auto_mode_builder, '_add_interactable')

    _auto_mode_builder.build()

    button = _auto_mode_builder._AutoModeBuilder__auto_mode_button  # noqa

    assert isinstance(button, QPushButton)
    assert button.text() == "A"
    assert button.objectName() == QObjectName.SquareButton

    mock_add_interactable.assert_called_once_with(button)

    # Assert 3: Button is added to the GUI layout
    simple_gui.top_left.layout().addWidget.assert_called_once_with(
        button, 0, 0,
        alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
    )


@pytest.mark.parametrize("is_auto_mode, expected_kind", [
    (True, QKind.Secondary),
    (False, QKind.Disabled),
])
def test_refresh_sets_button_style(mocker: MockerFixture, _auto_mode_builder, logger_mock, is_auto_mode, expected_kind,
                                   app_state_mock):
    """
    Test refresh() sets the correct QAttr.Kind based on app.state.is_auto_mode.
    """

    mock_button = mocker.MagicMock(spec=QPushButton)
    _auto_mode_builder._AutoModeBuilder__auto_mode_button = mock_button
    app_state_mock.is_auto_mode = is_auto_mode

    # Spy on polish
    mock_polish = mocker.patch.object(mock_button.style.return_value, 'polish')

    _auto_mode_builder.refresh()

    mock_button.setProperty.assert_called_once_with(QAttr.Kind, expected_kind)
    mock_polish.assert_called_once_with(mock_button)
    logger_mock.debug.assert_called_once()


def get_callback(button):
    """
    Helper to retrieve the connected callback function.
    """

    # Build the builder to ensure the callback is connected
    button.build()

    # The callback is connected to 'clicked'. The last connection is usually the one we want.
    # Since PyQt doesn't expose the function easily, we'll manually call the function
    # that button.clicked.emit() would execute.

    # For this test, we must manually trigger the callback logic rather than emulating
    # a signal emit, since the callback function is defined *inside* build().

    # We will patch the internal callback execution.
    # To test the logic, we must extract it. The easiest way is to mock the entire
    # build process and spy on the function defined inside.

    return button.__auto_mode_button.clicked.emit  # This is difficult in pure pytest.


@pytest.mark.parametrize("initial_state, expected_final_state, expected_notification", [
    (True, False, "Translated(notification_AutoModeOff)"),
    (False, True, "Translated(notification_AutoModeOn)"),
])
def test_button_callback_toggles_state_and_notifies(mocker: MockerFixture, _auto_mode_builder, notification_mock, qtbot,
                                                    app_state_mock, initial_state, expected_final_state,
                                                    expected_notification):
    """
    Test the button's callback function correctly toggles the state, notifies, and refreshes.
    """

    app_state_mock.is_auto_mode = initial_state

    # Spy on refresh (must be done after the builder is instantiated)
    mock_refresh = mocker.patch.object(_auto_mode_builder, 'refresh')

    # Call build() to set up the button and connect the callback
    _auto_mode_builder.build()
    button = _auto_mode_builder._AutoModeBuilder__auto_mode_button  # noqa

    # Act: Simulate button click
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    # Assert 1: State is toggled
    assert app_state_mock.is_auto_mode == expected_final_state

    # Assert 2: Refresh is called
    mock_refresh.assert_called_once()

    # Assert 3: Notification is called with the correct message
    notification_mock.assert_called_once_with(expected_notification)
