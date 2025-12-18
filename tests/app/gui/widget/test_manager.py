import pytest
from pytest_mock import MockerFixture


class TestManagerContext:

    def test_context_initialization(self, mocker: MockerFixture):

        from savegem.app.gui.widget.manager import ManagerContext

        mock_manager = mocker.Mock()
        mock_widget = mocker.Mock()
        mock_controller = mocker.Mock()

        controllers = {"test_ctrl": mock_controller}
        widgets = [mock_widget]

        context = ManagerContext(mock_manager, widgets, controllers)

        assert context.manager == mock_manager
        assert context.widgets == widgets
        assert context.controllers == controllers
        assert context.new_widgets == []
        assert context.removed_widgets == []

    def test_add_remove_widgets(self, mocker: MockerFixture):

        from savegem.app.gui.widget.manager import ManagerContext

        context = ManagerContext(mocker.Mock(), [], {})
        mock_w = mocker.Mock()

        context.add_widget(mock_w)
        assert mock_w in context.new_widgets

        context.remove_widget(mock_w)
        assert mock_w in context.removed_widgets


class TestWidgetManager:

    @pytest.fixture
    def _manager(self, gui_mock, module_patch):

        from savegem.app.gui.widget.manager import WidgetManager

        # Patch load_controllers to avoid external file loading
        module_patch("load_controllers", return_value={})
        return WidgetManager(gui_mock)

    @pytest.fixture
    def _create_widget(self, mocker: MockerFixture):

        def create_widget(section: str, name: str, order_id: int, parent = None):
            widget = mocker.MagicMock()
            widget.metadata.id = name
            widget.metadata.name = f"{section}.{name}"
            widget.metadata.section_id = section
            widget.metadata.order_id = order_id
            widget.metadata.parent = None
            widget.metadata.parent_widget_id = None
            widget.metadata.parent_widget_name = None

            if parent is not None:
                widget.metadata.parent_widget_id = parent.id
                widget.metadata.parent_widget_name = parent.name

            return widget

        return create_widget

    def test_execute_command_lifecycle(self, _manager, mocker: MockerFixture):

        from savegem.app.gui.widget.manager import WidgetManager

        # Mocking the Command
        mock_command = mocker.Mock()

        # Mocking internal add/remove methods to verify they are called
        # Using patch.object as discussed earlier for safety
        add_spy = mocker.patch.object(_manager, f"_{WidgetManager.__name__}__add_widgets")
        remove_spy = mocker.patch.object(_manager, f"_{WidgetManager.__name__}__remove_widgets")

        _manager.execute(mock_command)

        mock_command.execute.assert_called_once()
        add_spy.assert_called_once()
        remove_spy.assert_called_once()

    def test_build(self, mocker: MockerFixture, module_patch, _manager):

        # We patch the Command class itself
        build_command_mock = module_patch("WidgetBuildCommand")
        execute_mock = mocker.patch.object(_manager, "execute")

        meta_list = [mocker.Mock()]
        _manager.build(meta_list)

        build_command_mock.assert_called_once_with(meta_list)
        execute_mock.assert_called_once()

    def test_event_refresh(self, mocker: MockerFixture, module_patch, _manager):

        event_refresh_command_mock = module_patch("WidgetEventRefreshCommand")
        execute_mock = mocker.patch.object(_manager, "execute")

        event = "test"
        _manager.event_refresh(event)

        event_refresh_command_mock.assert_called_once_with(event)
        execute_mock.assert_called_once()

    @pytest.mark.parametrize("method, command", [
        ("refresh", "WidgetRefreshCommand"),
        ("enable", "WidgetEnableCommand"),
        ("disable", "WidgetDisableCommand"),
        ("delete", "WidgetDeleteCommand"),
    ])
    def test_execute_with_filter(self, mocker: MockerFixture, module_patch, _manager, method, command):

        # We patch the Command class itself
        command = module_patch(command)
        widget_filter = mocker.MagicMock()
        execute_mock = mocker.patch.object(_manager, "execute")
        execute_with_filter_spy = mocker.spy(_manager, "_WidgetManager__execute_with_filter")

        method = getattr(_manager, method)
        method(widget_filter)

        execute_with_filter_spy.assert_called_once_with(command, widget_filter)
        command.assert_called_once_with(widget_filter)
        execute_mock.assert_called_once_with(command.return_value)

        # No filter, should use default filter
        execute_with_filter_spy.reset_mock()
        command.reset_mock()
        execute_mock.reset_mock()
        method()

        execute_with_filter_spy.assert_called_once_with(command, None)
        execute_mock.assert_called_once_with(command.return_value)
        default_filter = command.call_args[0][0]

        # Verify that filter allows anything (basically any widget)
        assert default_filter(None) is True
        assert default_filter("str") is True
        assert default_filter(1) is True
        assert default_filter(False) is True
        assert default_filter({}) is True


    def test_get_widget(self, _manager, mocker: MockerFixture):

        mock_widget = mocker.Mock()
        # Accessing private dict for setup
        _manager._WidgetManager__widgets["section.id"] = mock_widget  # noqa

        assert _manager.get_widget("section", "id") == mock_widget
        assert _manager.get_widget("wrong", "id") is None

    def test_invoke_controllers(self, _manager, mocker: MockerFixture):

        mock_controller = mocker.Mock()
        _manager._WidgetManager__controllers = {"test_ctrl": mock_controller}

        mock_widget = mocker.Mock()
        mock_widget.metadata.controller = "test_ctrl"

        _manager.invoke_controllers("setup", [mock_widget])

        mock_controller.setup.assert_called_once_with(mock_widget)

    def test_invoke_controllers_without_controller(self, mocker: MockerFixture, _manager):

        mock_controller = mocker.Mock()
        _manager._WidgetManager__controllers = {"test_ctrl": mock_controller}

        mock_widget = mocker.Mock()
        mock_widget.metadata.controller = "non_existing"

        _manager.invoke_controllers("setup", [mock_widget])

        mock_controller.setup.assert_not_called()

    def test_add_widgets_ordering_and_root_parenting(self, mocker: MockerFixture, _manager, gui_mock, _create_widget):

        widget1 = _create_widget("section", "widget_1", 1)
        widget2 = _create_widget("section", "widget_2", 2)

        root_layout = gui_mock.root.layout.return_value
        invoke_controllers_mock = mocker.patch.object(_manager, "invoke_controllers")

        # Execute
        _manager._WidgetManager__add_widgets([widget2, widget1])  # noqa

        # Verify: w1 should be added before w2 due to order_id
        assert root_layout.addWidget.call_args_list[0][0][0] == widget1
        assert root_layout.addWidget.call_args_list[1][0][0] == widget2

        # Verify: Widget registry updated
        assert _manager._WidgetManager__widgets["section.widget_1"] == widget1  # noqa
        assert _manager._WidgetManager__widgets["section.widget_2"] == widget2  # noqa
        invoke_controllers_mock.assert_called_once_with("setup", [widget2, widget1])

    def test_add_widgets_nested_parenting(self, _manager, _create_widget):

        parent_widget = _create_widget("section", "parent_box", 1)
        _manager._WidgetManager__widgets[parent_widget.metadata.name] = parent_widget  # noqa

        child_widget = _create_widget("section", "child_btn", 1, parent_widget.metadata)
        parent_layout = parent_widget.layout.return_value

        # Execute
        _manager._WidgetManager__add_widgets([child_widget])  # noqa

        # Verify: Added to parent layout, not root
        parent_layout.add_widget.assert_called_once_with(child_widget)
        assert child_widget.metadata.parent == parent_widget.metadata

    def test_add_widgets_batch_parenting(self, _manager, _create_widget):
        # Setup: Both Parent and Child are in the same input list
        # Child has lower order_id but depends on Parent
        parent = _create_widget("section", "p1", order_id=1)
        child1 = _create_widget("section", "c1", order_id=2, parent=parent.metadata)
        child2 = _create_widget("section", "c2", order_id=1, parent=child1.metadata)

        _manager._WidgetManager__add_widgets([child1, child2, parent])  # noqa

        # Verify: Child correctly found parent in the 'widgets' list
        assert child1.metadata.parent == parent.metadata
        assert child2.metadata.parent == child1.metadata
        parent.layout.return_value.add_widget.assert_called_once_with(child1)
        child1.layout.return_value.add_widget.assert_called_once_with(child2)

    def test_remove_widgets_with_children(self, _manager, _create_widget):
        # Setup: A parent widget in the manager with mock children
        parent = _create_widget("section", "target", 1)
        child = _create_widget("section", "child", 1, parent=parent.metadata)
        non_existing_widget = _create_widget("section", "test", 1)

        # Register both in manager
        _manager._WidgetManager__widgets["section.target"] = parent  # noqa
        _manager._WidgetManager__widgets["section.child"] = child  # noqa

        # Mock findChildren to simulate Qt finding nested components
        parent.findChildren.return_value = [child, non_existing_widget]

        # Execute
        _manager._WidgetManager__remove_widgets([parent])  # noqa

        # Verify: Both parent and child removed from registry
        assert "section.target" not in _manager._WidgetManager__widgets  # noqa
        assert "section.child" not in _manager._WidgetManager__widgets  # noqa
        assert "section.test" not in _manager._WidgetManager__widgets  # noqa

        # Verify: Cleanup methods called
        parent.setParent.assert_called_once_with(None)
        parent.deleteLater.assert_called_once()
        child.setParent.assert_called_once_with(None)
        child.deleteLater.assert_called_once()
        non_existing_widget.setParent.assert_not_called()
        non_existing_widget.deleteLater.assert_not_called()
