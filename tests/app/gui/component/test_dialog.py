import pytest
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QDialog
from pytest_mock import MockerFixture


@pytest.fixture
def _parent_widget(qtbot):
    """
    Creates a dummy parent widget with fixed size.
    """

    widget = QWidget()
    widget.resize(1000, 800)
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def _dialog(_parent_widget, qtbot):
    """
    Creates the dialog attached to the parent.
    """

    from savegem.app.gui.component.dialog import QCustomDialog

    dialog_widget = QCustomDialog()
    dialog_widget.setParent(_parent_widget)
    dialog_widget.resize(200, 100)
    qtbot.addWidget(dialog_widget)

    return dialog_widget


@pytest.fixture
def _orphan_dialog(qtbot):

    from savegem.app.gui.component.dialog import QCustomDialog

    dialog_widget = QCustomDialog()
    qtbot.addWidget(dialog_widget)
    dialog_widget.resize(200, 100)

    return dialog_widget


@pytest.fixture
def _start_animation_mock(mocker: MockerFixture, _dialog, _orphan_dialog):
    start_mock = mocker.Mock()

    mocker.patch.object(_dialog._QCustomDialog__animation, "start", return_value=start_mock)  # noqa
    mocker.patch.object(_orphan_dialog._QCustomDialog__animation, "start", return_value=start_mock)  # noqa

    return start_mock


def test_initial_defaults(_dialog):
    """
    Test default property values and flags.
    """

    assert _dialog.top_offset == 0  # noqa
    assert _dialog.slide_duration == 250  # noqa
    assert _dialog.show_duration == 0  # noqa


def test_property_setters(_dialog):
    """
    Test setters update internal state and animation objects.
    """

    _dialog.top_offset = 50
    assert _dialog.top_offset == 50  # noqa

    _dialog.slide_duration = 500
    assert _dialog.slide_duration == 500  # noqa
    # Access private animation to verify duration update
    animation = _dialog._QCustomDialog__animation  # noqa
    assert animation.duration() == 500

    _dialog.show_duration = 3000
    assert _dialog.show_duration == 3000  # noqa


def test_show_no_parent(qtbot, _start_animation_mock):
    """
    Test that show returns early if no parent is set.
    """

    from savegem.app.gui.component.dialog import QCustomDialog

    orphan_dialog = QCustomDialog()
    qtbot.addWidget(orphan_dialog)
    orphan_dialog.show()

    _start_animation_mock.assert_not_called()


def test_show_geometry_calculation(_dialog, _parent_widget, _start_animation_mock):
    """
    Test the math for centering the dialog and slide-in positions.
    Parent: 1000x800
    Dialog: 200x100
    Top Offset: 50
    """

    _dialog.top_offset = 50

    # Expected X = (1000 - 200) // 2 = 400
    # Expected Y = 50 (top offset)
    expected_end_rect = QRect(400, 50, 200, 100)

    # Expected Start Y = -100 (negative height)
    expected_start_rect = QRect(400, -100, 200, 100)

    animation = _dialog._QCustomDialog__animation  # noqa

    _dialog.show()

    assert animation.startValue() == expected_start_rect
    assert animation.endValue() == expected_end_rect


def test_show_timer_logic(mocker: MockerFixture, _dialog):
    """
    Test that timer is set with correct duration (slide + show).
    """

    _dialog.slide_duration = 200
    _dialog.show_duration = 1000

    timer = _dialog._QCustomDialog__hide_timer  # noqa
    start_timer_mock = mocker.patch.object(timer, "start")

    _dialog.show()

    # Should be called with 200 + 1000 = 1200
    start_timer_mock.assert_called_once_with(1200)


def test_show_timer_ignored_if_zero(mocker: MockerFixture, _dialog):
    """
    Test that timer does NOT start if show_duration is 0.
    """

    _dialog.show_duration = 0
    timer = _dialog._QCustomDialog__hide_timer  # noqa
    start_timer_mock = mocker.patch.object(timer, "start")

    _dialog.show()
    start_timer_mock.assert_not_called()


def test_hide_animation_logic(_dialog, _start_animation_mock):
    """
    Test hide logic sets correct reverse geometry and connects close.
    """

    # Setup initial state (e.g., currently shown at 400, 50)
    current_rect = QRect(400, 50, 200, 100)
    _dialog.setGeometry(current_rect)

    anim = _dialog._QCustomDialog__animation  # Noqa

    # Expected End: Same X, Width, Height, but Y is -Height (-100)
    expected_end_rect = QRect(400, -100, 200, 100)

    _dialog.hide()

    assert anim.startValue() == current_rect
    assert anim.endValue() == expected_end_rect


def test_exec_calls_show(mocker: MockerFixture, _dialog):
    """
    Test that calling exec() triggers show() and adjustSize().
    """

    base_exec_mock = mocker.patch.object(QDialog, "exec")
    show_mock = mocker.patch.object(_dialog, "show")
    adjust_size_mock = mocker.patch.object(_dialog, "adjustSize")

    _dialog.exec()

    adjust_size_mock.assert_called_once()
    show_mock.assert_called_once()
    base_exec_mock.assert_called_once()
