import pytest
from PyQt6.QtWidgets import QWidget
from pytest_mock import MockerFixture


class TestCustomLayoutMixin:
    """
    Tests shared logic using QCustomVBoxLayout as the concrete implementation.
    """

    @pytest.fixture
    def _mock_widget_manager(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _parent_widget(self, mocker: MockerFixture, qtbot):
        """
        Creates a parent widget with mocked metadata.
        """

        from savegem.app.gui.component.widget import QCustomWidget

        widget = QCustomWidget()
        qtbot.addWidget(widget)

        metadata = mocker.MagicMock()
        metadata.id = "parent_section"
        metadata.raw_section_id = "section_1"
        metadata.grid_columns = 1

        widget.metadata = metadata

        return widget

    @pytest.fixture
    def _layout(self, _parent_widget, _mock_widget_manager):
        """
        Creates a layout attached to the parent widget.
        """

        from savegem.app.gui.component.layout import QCustomVBoxLayout

        layout = QCustomVBoxLayout()
        _parent_widget.setLayout(layout)
        layout.set_manager(_mock_widget_manager)
        return layout

    def test_set_manager(self, _layout, _mock_widget_manager):
        """
        Test manager assignment.
        """

        # Accessed via name mangling because it's private (__manager)
        assert getattr(_layout, "_CustomLayoutMixin__manager") == _mock_widget_manager

    def test_add_widget_basic(self, _layout, qtbot):
        """
        Test basic add_widget wrapper.
        """

        child = QWidget()
        qtbot.addWidget(child)

        _layout.add_widget(child)

        assert _layout.count() == 1
        assert _layout.itemAt(0).widget() == child

    def test_add_dynamic_widget_logic(self, module_patch, _layout, _parent_widget, _mock_widget_manager, qtbot):
        """
        Tests the heavy logic of add_dynamic_widget:
        1. Metadata creation
        2. ID generation
        3. Manager registration
        4. Recursion into child layouts
        """

        from savegem.app.gui.component.layout import QCustomHBoxLayout
        from savegem.app.gui.component.widget import QCustomWidget
        from savegem.app.gui.widget.metadata import WidgetMetadata

        # Create a child widget that DOES NOT have metadata yet
        child = QCustomWidget()
        qtbot.addWidget(child)

        # Give the child a layout to test recursion
        child_layout = QCustomHBoxLayout()
        child.setLayout(child_layout)
        get_widget_type_mock = module_patch("get_widget_type_by_class")

        _layout.add_dynamic_widget(child)

        assert hasattr(child, 'metadata')
        assert isinstance(child.metadata, WidgetMetadata)
        # Parent ID is 'parent_section', order is 1 -> 'parent_section_child1'
        assert child.metadata.id == "parent_section_child1"
        assert child.metadata.parent_widget_id == "parent_section"
        assert child.metadata.section_id == "section_1"
        assert child.metadata.order_id == 1
        assert child.metadata.widget_type == get_widget_type_mock.return_value

        _mock_widget_manager.add_widget.assert_called_once_with(child)

        # The child layout should now have the manager ref
        assert getattr(child_layout, "_CustomLayoutMixin__manager") == _mock_widget_manager

        assert _layout.count() == 1
        assert _layout.itemAt(0).widget() == child


class TestQCustomGridLayout:

    @pytest.fixture
    def _parent_widget(self, mocker: MockerFixture, qtbot):
        from savegem.app.gui.component.widget import QCustomWidget

        widget = QCustomWidget()
        qtbot.addWidget(widget)

        # Mock metadata with GRID COLUMNS support
        metadata_mock = mocker.MagicMock()
        metadata_mock.id = "grid_parent"

        widget.metadata = metadata_mock

        return widget

    def test_add_widget_grid_positioning(self, mocker: MockerFixture, _parent_widget, qtbot):
        """
        Tests that widgets are placed in correct Row/Col based on order_id
        and parent's grid_columns setting.
        """

        from savegem.app.gui.component.layout import QCustomGridLayout

        # Configure parent for 2 columns
        _parent_widget.metadata.grid_columns = 2  # noqa

        layout = QCustomGridLayout()
        _parent_widget.setLayout(layout)

        # Helper to create dummy children with preset order
        def create_child(order_id):
            w = QWidget()
            qtbot.addWidget(w)
            w.metadata = mocker.MagicMock()
            w.metadata.order_id = order_id
            return w

        # Create 3 widgets
        # Widget 1 -> Index 0 -> Row 0, Col 0
        w1 = create_child(1)
        # Widget 2 -> Index 1 -> Row 0, Col 1
        w2 = create_child(2)
        # Widget 3 -> Index 2 -> Row 1, Col 0 (Wrap around)
        w3 = create_child(3)

        # ACT
        layout.add_widget(w1)
        layout.add_widget(w2)
        layout.add_widget(w3)

        # ASSERT POSITIONS
        # getItemPosition returns (row, column, rowSpan, colSpan)

        # Check W1
        idx1 = layout.indexOf(w1)
        pos1 = layout.getItemPosition(idx1)
        assert pos1[:2] == (0, 0)  # Row 0, Col 0

        # Check W2
        idx2 = layout.indexOf(w2)
        pos2 = layout.getItemPosition(idx2)
        assert pos2[:2] == (0, 1)  # Row 0, Col 1

        # Check W3
        idx3 = layout.indexOf(w3)
        pos3 = layout.getItemPosition(idx3)
        assert pos3[:2] == (1, 0)  # Row 1, Col 0

    def test_column_stretch_applied(self, mocker: MockerFixture, _parent_widget, qtbot):
        """
        Test that setColumnStretch is called for configured columns.
        """

        from savegem.app.gui.component.layout import QCustomGridLayout

        _parent_widget.metadata.grid_columns = 3  # noqa
        layout = QCustomGridLayout()
        _parent_widget.setLayout(layout)

        w1 = QWidget()
        qtbot.addWidget(w1)
        w1.metadata = mocker.MagicMock()
        w1.metadata.order_id = 1

        mock_stretch = mocker.patch.object(layout, 'setColumnStretch')
        layout.add_widget(w1)

        assert mock_stretch.call_count == 3
        mock_stretch.assert_any_call(0, 1)
        mock_stretch.assert_any_call(1, 1)
        mock_stretch.assert_any_call(2, 1)
