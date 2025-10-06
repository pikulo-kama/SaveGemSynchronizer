import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QComboBox
from pytest_mock import MockerFixture

from savegem.app.gui.component.combobox import QCustomComboBox


@pytest.fixture
def _custom_combobox(qtbot):
    """
    Provides a QCustomComboBox instance registered with qtbot.
    """
    combobox = QCustomComboBox()
    combobox.addItems(["Item 1", "Item 2"])
    qtbot.addWidget(combobox)
    return combobox


def test_custom_combobox_initialization(_custom_combobox):
    """
    Test combobox initial state.
    """

    # Assert 1: Custom state variable defaults to True
    assert _custom_combobox._QCustomComboBox__is_enabled is True  # noqa

    # Assert 2: Standard QWidget enabled state is True (QComboBox default)
    # Note: QComboBox.isEnabled() might return True regardless of the custom logic,
    # but the internal variable __is_enabled controls the event handling.
    assert QComboBox.isEnabled(_custom_combobox) is True


def test_set_enabled_to_false_updates_state_and_attribute(mocker: MockerFixture, _custom_combobox):
    """
    Test setEnabled(False) updates the custom state and WA_Hover attribute.
    """

    mock_set_attribute = mocker.spy(_custom_combobox, 'setAttribute')

    _custom_combobox.setEnabled(False)

    assert _custom_combobox._QCustomComboBox__is_enabled is False  # noqa
    # Assert 2: WA_Hover is set to False (disabled)
    mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_Hover, False)


def test_set_enabled_to_true_updates_state_and_attribute(mocker: MockerFixture, _custom_combobox):
    """
    Test setEnabled(True) updates the custom state and WA_Hover attribute.
    """

    _custom_combobox.setEnabled(False)
    mock_set_attribute = mocker.spy(_custom_combobox, 'setAttribute')

    _custom_combobox.setEnabled(True)

    assert _custom_combobox._QCustomComboBox__is_enabled is True  # noqa
    mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_Hover, True)


def test_mouse_press_event_enabled_calls_super(mocker: MockerFixture, _custom_combobox):
    """
    Test mousePressEvent calls the base class handler when enabled.
    """

    _custom_combobox.setEnabled(True)
    mock_super = mocker.patch.object(QComboBox, 'mousePressEvent')
    mock_event = mocker.MagicMock(spec=QMouseEvent)

    _custom_combobox.mousePressEvent(mock_event)

    mock_super.assert_called_once_with(mock_event)
    mock_event.accept.assert_not_called()


def test_mouse_press_event_disabled_accepts_event(mocker: MockerFixture, _custom_combobox):
    """
    Test mousePressEvent accepts the event and blocks the base class handler when disabled.
    """

    _custom_combobox.setEnabled(False)
    mock_super = mocker.patch.object(QComboBox, 'mousePressEvent')
    mock_event = mocker.MagicMock(spec=QMouseEvent)

    _custom_combobox.mousePressEvent(mock_event)

    mock_event.accept.assert_called_once()
    mock_super.assert_not_called()


def test_key_press_event_enabled_calls_super(mocker: MockerFixture, _custom_combobox):
    """
    Test keyPressEvent calls the base class handler when enabled.
    """

    _custom_combobox.setEnabled(True)
    mock_super = mocker.patch.object(QComboBox, 'keyPressEvent')
    mock_event = mocker.MagicMock(spec=QKeyEvent)

    _custom_combobox.keyPressEvent(mock_event)

    # Assert 1: Super method is called
    mock_super.assert_called_once_with(mock_event)
    # Assert 2: Event is NOT explicitly accepted
    mock_event.accept.assert_not_called()


def test_key_press_event_disabled_accepts_event(mocker: MockerFixture, _custom_combobox):
    """
    Test keyPressEvent accepts the event and blocks the base class handler when disabled.
    """

    _custom_combobox.setEnabled(False)
    mock_super = mocker.patch.object(QComboBox, 'keyPressEvent')
    mock_event = mocker.MagicMock(spec=QKeyEvent)

    _custom_combobox.keyPressEvent(mock_event)

    # Assert 1: Event is explicitly accepted (blocking propagation)
    mock_event.accept.assert_called_once()
    # Assert 2: Super method is NOT called
    mock_super.assert_not_called()
