from typing import NamedTuple, Callable
from unittest.mock import MagicMock, ANY, PropertyMock
import pytest
from pytest_mock import MockerFixture


class MockCustomWidget(MagicMock):

    def __init__(self, metadata = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = metadata
        self.layout = MagicMock()
        self.enable = MagicMock()
        self.disable = MagicMock()
        self.refresh = MagicMock()
        self.setParent = MagicMock()
        self.deleteLater = MagicMock()
        self.setToolTip = MagicMock()
        self.setFixedWidth = MagicMock()
        self.setFixedHeight = MagicMock()
        self.apply_alignment = MagicMock()
        self.set_content = MagicMock()
        self.setStyleSheet = MagicMock()
        self.setProperty = MagicMock()


class MockMetadata(NamedTuple):
    id: str
    section_id: str
    name: str
    parent_widget_id: str
    parent_widget_name: str
    order_id: int
    controller: str = None
    widget_type: MagicMock = None
    layout_type: MagicMock = None
    refresh_events: list = []
    should_refresh_children: Callable = lambda event: False


class WidgetManagerTestModuleHelper:


    @pytest.fixture
    def _manager(self, gui_mock, module_patch):
        """
        Provides a WidgetManager instance with mocked dependencies.
        """

        from savegem.app.gui.widget.manager import WidgetManager

        module_patch("load_controllers", return_value={'CtrlA': MagicMock()})
        return WidgetManager(gui_mock)

    @staticmethod
    def _create_mock_widget(widget_id, section='root', parent_id=None, order=0, controller=None, refresh_events=None,
                            refresh_children=False):
        meta = MockMetadata(
            id=widget_id,
            section_id=section,
            name=f"{section}.{widget_id}",
            parent_widget_id=parent_id,
            parent_widget_name=f"{section}.{parent_id}" if parent_id else None,
            order_id=order,
            controller=controller,
            refresh_events=refresh_events or [],
            should_refresh_children=lambda event: refresh_children
        )

        return MockCustomWidget(meta=meta, metadata=meta)


class TestWidgetManagerBasic(WidgetManagerTestModuleHelper):

    def test_init(self, _manager, gui_mock):
        """
        Test initialization and property access.
        """

        widgets = _manager._WidgetManager__widgets  # noqa
        controllers = _manager._WidgetManager__controllers  # noqa

        assert _manager.gui == gui_mock
        assert isinstance(widgets, dict)
        assert 'CtrlA' in controllers

    def test_add_and_get_widget(self, _manager):
        """
        Test widget registration and lookup.
        """

        widget = self._create_mock_widget('my_btn', 'section_1')
        _manager.add_widget(widget)

        assert _manager.get_widget('section_1', 'my_btn') == widget
        assert _manager.get_widget('section_1', 'missing') is None


class TestWidgetManagerBuildFactory:

    def test_build_widget_success(self, mocker: MockerFixture, resolve_content_mock, gui_mock):
        """
        Tests the static factory method __build_widget.
        """

        from savegem.app.gui.component.layout import QCustomVBoxLayout
        from savegem.app.gui.widget.metadata import WidgetMetadata
        from savegem.app.gui.widget.manager import WidgetManager
        from savegem.common.db.table import DatabaseRow

        from_db_row_mock = mocker.patch.object(WidgetMetadata, "from_database_row")

        # 1. Setup Mock Metadata and Type
        mock_widget_type = mocker.MagicMock()
        mock_widget_type.type = PropertyMock(side_effect=MockCustomWidget)

        mock_layout_type = mocker.MagicMock()
        mock_layout_type.type = PropertyMock(side_effect=QCustomVBoxLayout)

        meta = mocker.MagicMock(
            widget_type=mock_widget_type,
            layout_type=mock_layout_type,
            content="Hello",
            tooltip="Tip",
            object_name="testName",
            stylesheet="color: red;",
            width=100,
            height=50,
            spacing=5,
            margin_left=1, margin_top=2, margin_right=3, margin_bottom=4,
            alignment=ANY,
            properties={"key": "val"},
            is_interactable=True
        )
        from_db_row_mock.return_value = meta
        resolve_content_mock.side_effect = lambda c: f"RESOLVED({c})"

        widget_row = DatabaseRow(1, (None,), ["id"])
        widget = WidgetManager._WidgetManager__build_widget(widget_row)  # noqa

        from_db_row_mock.assert_called_once_with(widget_row)
        mock_widget_type.type.assert_called_once()
        assert widget.metadata == meta

        # Check layout setup
        widget.setLayout.assert_called_once()
        widget.layout().setContentsMargins.assert_called_once_with(1, 2, 3, 4)
        widget.layout().setSpacing.assert_called_once_with(5)

        # Check content/tooltip resolution and assignment
        widget.set_content.assert_called_once_with("RESOLVED(Hello)")
        widget.setToolTip.assert_called_once_with("RESOLVED(Tip)")

        # Check styling and properties
        widget.setObjectName.assert_called_once_with("testName")
        widget.setStyleSheet.assert_called_once_with("color: red;")
        widget.setProperty.assert_called_once_with("key", "val")
        widget.setFixedWidth.assert_called_once_with(100)
        widget.setFixedHeight.assert_called_once_with(50)
        widget.apply_alignment.assert_called_once()


class TestWidgetManagerBuild(WidgetManagerTestModuleHelper):

    # Patch the factory and database globally for this section
    def test_build_root_section_flow(self, mocker: MockerFixture, _manager, db_mock, gui_mock):
        """
        Tests building the root section, including database query and linking.
        """

        from savegem.app.gui.widget.manager import WidgetManager
        from savegem.app.gui.constants import UISection
        from savegem.common.db.table import DatabaseRow

        mock_build_widget = mocker.patch.object(WidgetManager, '_WidgetManager__build_widget')

        db_mock.table.return_value.retrieve.return_value = [
            DatabaseRow(1, ("w1", 1), ["id", "order_id"]),
            DatabaseRow(1, ("w2", 2), ["id", "order_id"])
        ]

        # 2. Setup Mock Built Widgets (The widgets must be sorted by order_id)
        # Widget A (Parent: None, Order: 1)
        meta_a = MockMetadata(
            id='w1',
            section_id='root',
            name='root.w1',
            parent_widget_id=None,  # noqa
            parent_widget_name="None.w1",
            order_id=1
        )
        widget_a = MockCustomWidget(meta_a, layout=MagicMock())
        widget_a.layout.return_value = MagicMock()

        # Widget B (Parent: A, Order: 2)
        meta_b = MockMetadata(
            id='w2',
            section_id='root',
            name='root.w2',
            parent_widget_id='w1',
            parent_widget_name='root.w1',
            order_id=2
        )
        widget_b = MockCustomWidget(meta_b, layout=MagicMock())
        widget_b.layout.return_value = MagicMock()

        mock_build_widget.side_effect = [widget_a, widget_b]

        # 3. ACT
        _manager.build(section_id=UISection.RootSection)

        # 4. ASSERTIONS

        # Check database query (RootSection should use IS NULL)
        db_mock.table.assert_called_once_with("ui_widgets")
        db_mock.table.return_value.where.assert_called_once_with("section_id IS NULL")

        # Check widget manager setup (manager propagation to layout)
        widget_a.layout().set_manager.assert_called_once_with(_manager)
        widget_b.layout().set_manager.assert_called_once_with(_manager)

        # Check linking/ordering logic

        # Widget A (Order 1, Parent None) added to GUI root layout
        gui_mock.root.layout().addWidget.assert_called_once_with(widget_a)

        # Widget B (Order 2, Parent A) added to Widget A's layout
        widget_a.layout().add_widget.assert_called_once_with(widget_b)

        # Check controllers setup invoked
        assert gui_mock.root.layout().addWidget.call_count == 1
        assert _manager.get_widget('root', 'w1') == widget_a


    def test_build_specific_section_flow(self, mocker: MockerFixture, _manager, db_mock):
        """
        Tests building a non-root section.
        """

        from savegem.app.gui.widget.manager import WidgetManager
        from savegem.common.db.table import DatabaseRow

        mock_build_widget = mocker.patch.object(WidgetManager, '_WidgetManager__build_widget')

        db_mock.table.return_value.retrieve.return_value = [DatabaseRow(1, ("w1",), ["id"])]
        mock_build_widget.return_value = self._create_mock_widget('w1', 'specific_section')

        # Simulate scenario when there are already widgets in manager.
        _manager.add_widget(self._create_mock_widget("test", controller="Test"))

        _manager.build(section_id='specific_section')

        # Check database query (Specific section should use 'section_id = ?')
        db_mock.table.assert_called_once_with("ui_widgets")
        db_mock.table.return_value.where.assert_called_once_with("section_id = ?", "specific_section")


class TestWidgetManagerLifecycle(WidgetManagerTestModuleHelper):

    @pytest.fixture
    def _mock_widgets(self, _manager):
        """
        Helper to populate the manager with widgets for lifecycle testing.
        """

        from savegem.app.gui.constants import UIRefreshEvent

        # Widget 1: Needs refresh for ALL and custom event
        first_widget = self._create_mock_widget(
            'w1',
            's1',
            controller='CtrlA',
            refresh_events=[UIRefreshEvent.All, 'CUSTOM'],
            refresh_children=True
        )

        # Widget 2: Needs refresh for only ALL
        second_widget = self._create_mock_widget(
            'w2',
            's1',
            controller='CtrlA',
            refresh_events=[UIRefreshEvent.All]
        )

        # Widget 3: No controller, only refreshes on CUSTOM (and ALL)
        third_widget = self._create_mock_widget(
            'w3',
            's2',
            controller=None,
            refresh_events=[UIRefreshEvent.All, 'CUSTOM'],
            refresh_children=False
        )

        _manager.add_widget(first_widget)
        _manager.add_widget(second_widget)
        _manager.add_widget(third_widget)

        return first_widget, second_widget, third_widget


    def test_enable(self, _manager, mocker, _mock_widgets):
        """
        Test enabling widgets and invoking controllers.
        """

        mock_ctrl_a = MagicMock()
        mocker.patch.dict(_manager._WidgetManager__controllers, {'CtrlA': mock_ctrl_a})  # noqa

        _manager.enable()

        # Check widget calls
        _mock_widgets[0].enable.assert_called_once()
        _mock_widgets[1].enable.assert_called_once()
        _mock_widgets[2].enable.assert_called_once()

        # Check controller calls (CtrlA assigned to first and second)
        mock_ctrl_a.enable.assert_any_call(_mock_widgets[0])
        mock_ctrl_a.enable.assert_any_call(_mock_widgets[1])
        assert mock_ctrl_a.enable.call_count == 2  # w3 has no controller


    def test_disable(self, _manager, mocker, _mock_widgets):
        """
        Test enabling widgets and invoking controllers.
        """

        mock_ctrl_a = MagicMock()
        mocker.patch.dict(_manager._WidgetManager__controllers, {'CtrlA': mock_ctrl_a})  # noqa

        _manager.disable()

        # Check widget calls
        _mock_widgets[0].disable.assert_called_once()
        _mock_widgets[1].disable.assert_called_once()
        _mock_widgets[2].disable.assert_called_once()

        # Check controller calls (CtrlA assigned to first and second)
        mock_ctrl_a.disable.assert_any_call(_mock_widgets[0])
        mock_ctrl_a.disable.assert_any_call(_mock_widgets[1])
        assert mock_ctrl_a.disable.call_count == 2  # w3 has no controller


    def test_refresh_all(self, _manager, _mock_widgets):
        """
        Test general refresh (UIRefreshEvent.All).
        """

        from savegem.app.gui.constants import UIRefreshEvent

        _manager.refresh(UIRefreshEvent.All)

        # All widgets should be refreshed because ALL is always in refresh_events (init logic)
        _mock_widgets[0].refresh.assert_called_once_with(refresh_children=True)
        _mock_widgets[1].refresh.assert_called_once_with(refresh_children=False)
        _mock_widgets[2].refresh.assert_called_once_with(refresh_children=False)


    def test_refresh_custom_with_children(self, _manager, _mock_widgets):
        """
        Test specific refresh event, checking refresh_children logic.
        """

        _manager.refresh("CUSTOM")

        # w1: Refreshed recursively because it's configured for CUSTOM (and metadata mock is True)
        _mock_widgets[0].refresh.assert_called_once_with(refresh_children=True)
        # w2: Ignored, not in its refresh_events (only ALL)
        _mock_widgets[1].refresh.assert_not_called()
        # w3: Refreshed non-recursively because it's configured for CUSTOM (and default meta mock is False)
        _mock_widgets[2].refresh.assert_called_once_with(refresh_children=False)


class TestWidgetManagerRemoval(WidgetManagerTestModuleHelper):

    def test_remove_widgets_by_condition(self, mocker: MockerFixture, _manager):
        """
        Test removal of widgets matching a condition, including controller reset.
        """

        # Setup widgets (w1 is parent, w2 is child, w3 is unrelated)
        w1 = self._create_mock_widget('w1', 's1', controller='CtrlA')
        w2 = self._create_mock_widget('w2', 's1', parent_id='w1', order=1, controller='CtrlB')
        w3 = self._create_mock_widget('w3', 's2', controller='CtrlA')

        _manager.add_widget(w1)
        _manager.add_widget(w2)
        _manager.add_widget(w3)

        mock_ctrl_a = MagicMock()
        mock_ctrl_b = MagicMock()
        mocker.patch.dict(_manager._WidgetManager__controllers, {  # noqa
            "CtrlA": mock_ctrl_a,
            "CtrlB": mock_ctrl_b
        })

        # ACT: Remove all widgets in section 's1' (w1 and w2)
        _manager.remove_widgets(lambda meta: meta.section_id == 's1')

        # ASSERT WIDGET REMOVAL

        # w1 and w2 removed, w3 remains
        assert _manager.get_widget('s1', 'w1') is None
        assert _manager.get_widget('s1', 'w2') is None
        assert _manager.get_widget('s2', 'w3') == w3
        assert len(_manager._WidgetManager__widgets) == 1  # noqa

        # ASSERT WIDGET CLEANUP

        # w1 and w2 should have their parents removed and deleteLater called
        w1.setParent.assert_called_once_with(None)
        w1.deleteLater.assert_called_once()
        w2.setParent.assert_called_once_with(None)
        w2.deleteLater.assert_called_once()

        # ASSERT CONTROLLER RESET (CtrlA used by w1 and w3, CtrlB used by w2)

        # w1 reset CtrlA (should only happen once per controller type)
        # w2 reset CtrlB
        mock_ctrl_a.reset_state.assert_called()  # Called for w1 (s1)
        mock_ctrl_b.reset_state.assert_called()  # Called for w2 (s1)


    def test_remove_child_widgets(self, mocker: MockerFixture, _manager):
        """
        Test the high-level API for removing children of a single widget.
        """

        # Setup
        w_parent = self._create_mock_widget('P', 's1')
        w_child_1 = self._create_mock_widget('C1', 's1', parent_id='P')
        w_child_2 = self._create_mock_widget('C2', 's1', parent_id='P')

        _manager.add_widget(w_parent)
        _manager.add_widget(w_child_1)
        _manager.add_widget(w_child_2)

        # ACT: Remove children of w_parent
        remove_widgets_mock =mocker.patch.object(_manager, "remove_widgets")
        _manager.remove_child_widgets(w_parent)

        # ASSERT: Should call remove_widgets with the correct filtering function
        remove_widgets_mock.assert_called_once()

        # Manually check the lambda passed to ensure it targets the correct parent name
        clear_condition = remove_widgets_mock.call_args[0][0]

        assert clear_condition(w_child_1.metadata) is True  # Child matches
        assert clear_condition(w_parent.metadata) is False  # Parent does NOT match
