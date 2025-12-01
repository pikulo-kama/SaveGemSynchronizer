import pytest
from unittest.mock import MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from pytest_mock import MockerFixture


@pytest.fixture
def _test_widget_class():
    from savegem.app.gui.component import CustomComponentMixin

    class TestWidget(QWidget, CustomComponentMixin):
        def __init__(self, parent=None):

            QWidget.__init__(self, parent)
            CustomComponentMixin.__init__(self)

        # Override set_content to verify it gets called
        def set_content(self, content):
            pass

    return TestWidget


@pytest.fixture
def _test_widget(qtbot, _test_widget_class, _mock_metadata):
    """
    Creates a TestWidget instance with metadata set.
    """

    widget = _test_widget_class()
    qtbot.addWidget(widget)
    widget.metadata = _mock_metadata

    return widget


@pytest.fixture
def _test_child_widget(qtbot, _test_widget_class, _test_widget):
    """
    Creates a child TestWidget instance.
    """

    child_widget = _test_widget_class(parent=_test_widget)
    qtbot.addWidget(child_widget)

    return child_widget


@pytest.fixture
def _mock_metadata(mocker: MockerFixture):
    """
    Creates a mock WidgetMetadata object.
    """

    metadata = mocker.MagicMock()
    metadata.name = "TestWidget"

    # Default behavior: interactable
    type_mock = MagicMock()
    type_mock.is_interactable = True
    metadata.widget_type = type_mock
    metadata.alignment = Qt.AlignmentFlag.AlignLeft
    metadata.content = "some_content_key"
    metadata.tooltip = "some_tooltip_key"

    return metadata


def test_metadata_getter_setter(mocker: MockerFixture, qtbot, _test_widget_class):
    """
    Test that metadata property works correctly.
    """

    widget = _test_widget_class()
    qtbot.addWidget(widget)

    assert widget.metadata is None

    mock_meta = mocker.MagicMock()
    widget.metadata = mock_meta

    assert widget.metadata == mock_meta


def test_apply_alignment_with_layout(mocker: MockerFixture, _test_widget, _mock_metadata):
    """
    Test applying alignment when a layout exists.
    """

    layout = QVBoxLayout()
    set_alignment_mock = mocker.Mock()
    layout.setAlignment = set_alignment_mock

    _test_widget.setLayout(layout)

    _test_widget.apply_alignment()
    set_alignment_mock.assert_called_once_with(_mock_metadata.alignment)


def test_apply_alignment_no_layout(_test_widget):
    """
    Test applying alignment when no layout exists (should not crash).
    """

    assert _test_widget.layout() is None

    try:
        _test_widget.apply_alignment()
    except Exception as e:
        pytest.fail(f"apply_alignment raised exception without layout: {e}")


def test_enable_interactable(_test_widget, _mock_metadata):
    """
    Test enable() when widget is interactable.
    """

    _mock_metadata.widget_type.is_interactable = True
    _test_widget.setEnabled(False)  # Start disabled

    _test_widget.enable()

    assert _test_widget.isEnabled() is True
    assert _test_widget.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_enable_non_interactable(_test_widget, _mock_metadata):
    """
    Test enable() when widget is NOT interactable.
    """

    _mock_metadata.widget_type.is_interactable = False
    _test_widget.setEnabled(False)

    _test_widget.enable()

    # Should remain disabled or unchanged based on logic,
    # but specifically setEnabled(True) is NOT called inside the if block.
    # However, since we track state change:
    assert _test_widget.isEnabled() is False


def test_disable_interactable(_test_widget, _mock_metadata):
    """
    Test disable() when widget is interactable.
    """

    _mock_metadata.widget_type.is_interactable = True
    _test_widget.setEnabled(True)

    _test_widget.disable()

    assert _test_widget.isEnabled() is False
    assert _test_widget.cursor().shape() == Qt.CursorShape.WaitCursor


def test_refresh_no_metadata(_test_widget, _mock_metadata, resolve_content_mock):
    """
    Test refresh returns early if metadata is None.
    """

    _mock_metadata.content = None
    _mock_metadata.tooltip = None

    # If metadata is None, resolve_content should never be called
    _test_widget.refresh()
    resolve_content_mock.assert_not_called()


def test_refresh_content_and_tooltip(mocker: MockerFixture, _test_widget, _mock_metadata, resolve_content_mock):
    """
    Test refresh calls resolve_content and updates tooltip.
    """

    _mock_metadata.content = "Content"
    _mock_metadata.tooltip = "Tooltip"

    # Mock the resolve_content function
    # NOTE: Update 'savegem.app.gui.widget.resolver' path if the import in your file differs
    resolve_content_mock.side_effect = ["Resolved Content", "Resolved Tooltip"]

    mock_set_content = mocker.Mock()
    _test_widget.set_content = mock_set_content

    _test_widget.refresh()

    assert resolve_content_mock.call_count == 2  # Once for content, once for tooltip
    mock_set_content.assert_called_once_with("Resolved Content")
    assert _test_widget.toolTip() == "Resolved Tooltip"


def test_refresh_recursive(mocker: MockerFixture, _test_widget_class, _test_widget, _mock_metadata, _test_child_widget):
    """
    Test refresh calls refresh() on child widgets.
    """

    _mock_metadata.content = None
    _mock_metadata.tooltip = None

    mock_child_refresh = mocker.patch.object(_test_child_widget, 'refresh')

    _test_widget.refresh(refresh_children=True)
    mock_child_refresh.assert_called_once()


def test_update_styles(mocker: MockerFixture, _test_widget, _test_child_widget):
    """
    Test update_styles polishes self and recurses to children.
    """

    mock_style = mocker.patch.object(_test_widget, "style")
    mock_child_update = mocker.patch.object(_test_child_widget, "update_styles")

    _test_widget.update_styles()

    # Verify polish was called on self
    mock_style.return_value.polish.assert_called_with(_test_widget)

    # Verify recursion
    mock_child_update.assert_called_once()


def test_should_not_refresh_if_not_metadata(mocker: MockerFixture, _test_widget, _test_child_widget):

    _test_widget.metadata = None
    child_refresh_mock = mocker.patch.object(_test_child_widget, "refresh")

    _test_widget.refresh(refresh_children=True)

    child_refresh_mock.assert_not_called()
