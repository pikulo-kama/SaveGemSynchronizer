import pytest
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture

from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.constants import QAttr, QBool


@pytest.fixture
def _custom_button(qtbot):
    """
    Provides a QCustomPushButton instance registered with qtbot.
    """

    button = QCustomPushButton("Test")
    qtbot.addWidget(button)

    return button


def test_custom_push_button_initialization(_custom_button):
    """
    Test the button's initial state and custom properties.
    """

    assert _custom_button._QCustomPushButton__is_enabled is True  # noqa
    assert _custom_button.property(QAttr.Disabled) == QBool(False)
    assert QPushButton.isEnabled(_custom_button) is True


def test_set_enabled_to_false_updates_state_and_property(mocker: MockerFixture, _custom_button):
    """
    Test setEnabled(False) updates the custom state and property.
    """

    mock_polish = mocker.patch.object(_custom_button.style(), 'polish')

    _custom_button.setEnabled(False)

    assert _custom_button._QCustomPushButton__is_enabled is False  # noqa
    assert _custom_button.property(QAttr.Disabled) == QBool(True)

    mock_polish.assert_called_once_with(_custom_button)


def test_set_enabled_to_true_updates_state_and_property(mocker: MockerFixture, _custom_button):
    """
    Test setEnabled(True) updates the custom state and property.
    """

    _custom_button.setEnabled(False)
    mock_polish = mocker.patch.object(_custom_button.style(), 'polish')

    _custom_button.setEnabled(True)

    assert _custom_button._QCustomPushButton__is_enabled is True  # noqa
    assert _custom_button.property(QAttr.Disabled) == QBool(False)
    mock_polish.assert_called_once_with(_custom_button)


def test_mouse_press_event_enabled_calls_super(mocker: MockerFixture, _custom_button):
    """
    Test mousePressEvent calls the base class handler when enabled.
    """

    _custom_button.setEnabled(True)
    mock_super = mocker.patch.object(QPushButton, 'mousePressEvent')
    mock_event = mocker.MagicMock(spec=QMouseEvent)

    _custom_button.mousePressEvent(mock_event)

    mock_super.assert_called_once_with(mock_event)
    mock_event.accept.assert_not_called()


def test_mouse_press_event_disabled_accepts_event(mocker: MockerFixture, _custom_button):
    """
    Test mousePressEvent accepts the event and blocks the base class handler when disabled.
    """

    _custom_button.setEnabled(False)
    mock_super = mocker.patch.object(QPushButton, 'mousePressEvent')
    mock_event = mocker.MagicMock(spec=QMouseEvent)

    _custom_button.mousePressEvent(mock_event)

    mock_event.accept.assert_called_once()
    mock_super.assert_not_called()


def test_key_press_event_enabled_calls_super(mocker: MockerFixture, _custom_button):
    """
    Test keyPressEvent calls the base class handler when enabled.
    """

    _custom_button.setEnabled(True)
    mock_super = mocker.patch.object(QPushButton, 'keyPressEvent')
    mock_event = mocker.MagicMock(spec=QKeyEvent)

    _custom_button.keyPressEvent(mock_event)

    mock_super.assert_called_once_with(mock_event)
    mock_event.accept.assert_not_called()


def test_key_press_event_disabled_accepts_event(mocker: MockerFixture, _custom_button):
    """
    Test keyPressEvent accepts the event and blocks the base class handler when disabled.
    """

    # Arrange: Disable the button
    _custom_button.setEnabled(False)
    mock_super = mocker.patch.object(QPushButton, 'keyPressEvent')
    mock_event = mocker.MagicMock(spec=QKeyEvent)

    _custom_button.keyPressEvent(mock_event)

    mock_event.accept.assert_called_once()
    mock_super.assert_not_called()
