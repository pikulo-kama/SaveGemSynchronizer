import pytest
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QProgressBar
from pytest_mock import MockerFixture

from savegem.app.gui.component.button import QCustomPushButton
from savegem.app.gui.component.progress_button import QProgressPushButton
from savegem.app.gui.constants import QAttr, QBool


@pytest.fixture
def _progress_button(qtbot):
    """
    Provides a QProgressPushButton instance registered with qtbot.
    """

    button = QProgressPushButton("Download")
    button.resize(200, 50)
    qtbot.addWidget(button)

    return button


def test_progress_button_initialization(_progress_button):
    """
    Test the button initializes the progress bar correctly.
    """

    assert isinstance(_progress_button, QCustomPushButton)

    progress_bar = _progress_button._QProgressPushButton__progress_bar  # noqa
    assert isinstance(progress_bar, QProgressBar)
    assert progress_bar.parent() is _progress_button

    assert progress_bar.value() == 0
    assert progress_bar.isTextVisible() is False

    assert _progress_button.property("in-progress") is None  # Property is set in set_progress


@pytest.mark.parametrize("progress, expected_in_progress, expected_enabled", [
    (10, True, False),  # In progress: Should be disabled
    (50, True, False),
    (100, True, False),
    (0, False, True),  # Not in progress: Should be enabled
])
def test_set_progress_updates_state_and_properties(_progress_button, progress, expected_in_progress, expected_enabled):
    """

    Test set_progress updates QProgressBar value, text, custom property, and enabled state.
    """

    progress_bar = _progress_button._QProgressPushButton__progress_bar  # noqa
    original_text = _progress_button.text()

    _progress_button.set_progress(progress)

    assert progress_bar.value() == progress
    assert _progress_button.property("in-progress") == QBool(expected_in_progress)
    assert _progress_button._QCustomPushButton__is_enabled == expected_enabled  # noqa

    if expected_in_progress:
        # If in progress, text should be cleared and progress bar text visible
        assert _progress_button.text() == ""
        assert progress_bar.isTextVisible() is True

    else:
        # If finished, button text should be preserved (or remain as it was)
        assert _progress_button.text() == original_text
        assert progress_bar.isTextVisible() is False


def test_set_property_propagates_kind_to_progress_bar(_progress_button):
    """
    Test setProperty propagates QAttr.Kind to the progress bar with the correct prefixed value.
    """

    test_kind = "Primary"
    progress_bar = _progress_button._QProgressPushButton__progress_bar  # noqa
    expected_bar_kind = f"QProgressPushButton-{test_kind}"

    _progress_button.setProperty(QAttr.Kind, test_kind)

    assert _progress_button.property(QAttr.Kind) == test_kind
    assert progress_bar.property(QAttr.Kind) == expected_bar_kind


def test_set_property_does_not_propagate_other_attributes(_progress_button):
    """
    Test setProperty only propagates QAttr.Kind and ignores others.
    """

    test_attr = "SomeOtherAttribute"
    test_value = "TestValue"
    progress_bar = _progress_button._QProgressPushButton__progress_bar  # noqa

    _progress_button.setProperty(test_attr, test_value)

    assert _progress_button.property(test_attr) == test_value
    assert progress_bar.property(test_attr) is None


def test_resize_event_updates_progress_bar_geometry(mocker: MockerFixture, _progress_button):
    """
    Test that resizeEvent sets the progress bar's geometry to match the button.
    """

    mock_super_resize = mocker.spy(QCustomPushButton, 'resizeEvent')

    new_width, new_height = 350, 80
    new_size = QSize(new_width, new_height)

    _progress_button.resize(new_size)
    _progress_button.resizeEvent(QResizeEvent(new_size, QSize(200, 50)))

    progress_bar = _progress_button._QProgressPushButton__progress_bar  # noqa

    mock_super_resize.assert_called()
    assert progress_bar.x() == 0
    assert progress_bar.y() == 0
    assert progress_bar.width() == new_width
    assert progress_bar.height() == new_height
