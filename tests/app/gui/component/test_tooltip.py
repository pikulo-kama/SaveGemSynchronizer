import pytest
from PyQt6.QtCore import Qt


@pytest.fixture
def _tooltip(qtbot):
    """
    Fixture to provide a fresh QIconTooltip instance for each test.
    """

    from savegem.app.gui.component.tooltip import QIconTooltip

    tooltip = QIconTooltip()
    qtbot.addWidget(tooltip)

    return tooltip


def test_initialization_visible_text(_tooltip):
    """
    The visible text should be set to '!'.
    """

    assert _tooltip.text() == "!"


def test_initialization_object_name(_tooltip):
    """
    The object name should be set correctly for styling.
    """

    from savegem.app.gui.constants import QObjectName
    assert _tooltip.objectName() == QObjectName.InformationIcon


def test_initialization_alignment(_tooltip):
    """
    The visible text should be centered.
    """

    # Qt.AlignmentFlag.AlignCenter is the expected value
    expected_alignment = Qt.AlignmentFlag.AlignCenter
    assert _tooltip.alignment() == expected_alignment


def test_initialization_cursor(_tooltip):
    """
    The cursor should be set to WhatsThisCursor for information access.
    """

    # Check the cursor shape value
    expected_cursor = Qt.CursorShape.WhatsThisCursor
    assert _tooltip.cursor().shape() == expected_cursor


def test_set_text_sets_tooltip(_tooltip):
    """
    Calling setText(message) should correctly set the tooltip message.
    """

    test_message = "This is a test disclaimer."
    _tooltip.setText(test_message)

    # In PyQt, the tooltip is retrieved via the tooltip() method
    assert _tooltip.toolTip() == test_message
