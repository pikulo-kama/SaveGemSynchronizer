import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from PyQt6.QtWidgets import QComboBox, QStyleOptionViewItem, QStyle, QStyledItemDelegate
from pytest_mock import MockerFixture


@pytest.fixture
def _custom_combobox(qtbot):
    """
    Provides a QCustomComboBox instance registered with qtbot.
    """

    from savegem.app.gui.component.combobox import QCustomComboBox

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


def test_show_popup(mocker: MockerFixture, _custom_combobox):

    from savegem.app.gui.component.combobox import NoFocusDelegate

    view_mock = mocker.patch.object(_custom_combobox, "view")
    set_delegate_mock = view_mock.return_value.setItemDelegate
    set_cursor_mock = view_mock.return_value.viewport.return_value.setCursor

    _custom_combobox.showPopup()

    set_cursor_mock.assert_called_once_with(Qt.CursorShape.PointingHandCursor)
    set_delegate_mock.assert_called_once()

    delegate = set_delegate_mock.call_args[0][0]
    assert isinstance(delegate, NoFocusDelegate)


def test_paint_removes_focus_state(mocker: MockerFixture, painter_mock):
    """
    Verifies that if the option has State_HasFocus, it is removed
    before calling the parent paint method.
    """

    from savegem.app.gui.component.combobox import NoFocusDelegate

    # Create a real QStyleOptionViewItem (easier than mocking bitwise operations)
    delegate = NoFocusDelegate()
    option = QStyleOptionViewItem()
    index_mock = mocker.Mock()

    # Set up a state that includes HasFocus AND some other flag (e.g., Enabled)
    # We want to ensure Focus is removed but Enabled stays.
    initial_state = QStyle.StateFlag.State_HasFocus | QStyle.StateFlag.State_Enabled
    option.state = initial_state

    # We patch the PARENT class's paint method.
    # This allows us to see what arguments 'super().paint()' received.
    base_paint_mock = mocker.patch.object(QStyledItemDelegate, "paint")

    delegate.paint(painter_mock, option, index_mock)

    # 1. Assert parent was called
    base_paint_mock.assert_called_once()

    # 2. Get the 'option' object passed to the parent
    # args[0] is 'self' (because we patched the class), args[1] is painter, args[2] is option
    passed_option = base_paint_mock.call_args[0][1]

    # 3. VERIFY: State_HasFocus should be GONE
    assert not (passed_option.state & QStyle.StateFlag.State_HasFocus)

    # 4. VERIFY: Other flags (State_Enabled) should REMAIN
    assert passed_option.state & QStyle.StateFlag.State_Enabled


def test_paint_leaves_other_states_alone(mocker: MockerFixture, painter_mock):
    """
    Verifies that if the option does NOT have focus, the state is untouched.
    """

    from savegem.app.gui.component.combobox import NoFocusDelegate

    delegate = NoFocusDelegate()
    option = QStyleOptionViewItem()
    index_mock = mocker.Mock()

    # Set state to just Enabled (No Focus)
    initial_state = QStyle.StateFlag.State_Enabled
    option.state = initial_state

    base_paint_mock = mocker.patch.object(QStyledItemDelegate, "paint")

    delegate.paint(painter_mock, option, index_mock)

    # Verify state is exactly what it was before
    passed_option = base_paint_mock.call_args[0][1]
    assert passed_option.state == initial_state
