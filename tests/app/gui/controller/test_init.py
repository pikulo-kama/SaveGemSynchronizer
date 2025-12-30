from unittest.mock import MagicMock, call
import pytest
from pytest_mock import MockerFixture

from savegem.app.gui.widget.command.build import WidgetSectionBuildCommand


class TestWidgetController:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture, db_table_mock):
        # Configure DB to return a non-empty result for initialization
        db_table_mock.is_empty = False
        db_table_mock.rows = [mocker.MagicMock()]

    @pytest.fixture
    def _mock_controller(self):
        from savegem.app.gui.controller import WidgetController

        class MockController(WidgetController):
            """A concrete controller subclass for testing reflection."""

            def __init__(self, manager):
                super().__init__(manager)
                self.load_sections = MagicMock()

        return MockController

    @pytest.fixture
    def _widget_manager(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def mock_controller(self, widget_manager_mock, db_table_mock):
        """
        Provides a fresh WidgetController instance.
        """

        from savegem.app.gui.controller import WidgetController

        return WidgetController(widget_manager_mock)

    def test_load_controllers_reflection(self, _mock_controller, get_members_mock, _widget_manager, logger_mock):
        """
        Tests that load_controllers finds subclasses via reflection and instantiates them.
        """

        from savegem.app.gui.controller import load_controllers, TemplateWidgetController

        def _get_members(_, __):
            yield "MockController", _mock_controller
            yield "TemplateWidgetController", TemplateWidgetController

        get_members_mock.side_effect = _get_members

        controllers = load_controllers(_widget_manager)
        mocked_controller = controllers['MockController']

        assert len(controllers) == 1
        assert 'MockController' in controllers
        assert isinstance(mocked_controller, _mock_controller)
        assert mocked_controller.manager == _widget_manager
        mocked_controller.load_sections.assert_called_once()

        # Assert debug logging happened
        logger_mock.isEnabledFor.return_value = True
        # The debug call checks that the list of keys was logged
        logger_mock.debug.assert_any_call("Controllers have been loaded: %s", "MockController")

    def test_load_sections(self, db_mock, db_table_mock, _widget_manager):
        """
        Test initialization correctly queries the database for sections.
        """

        from savegem.app.gui.controller import WidgetController

        # ACT: Initialize a generic controller
        controller = WidgetController(_widget_manager)
        controller.load_sections()

        # ASSERT DB CALLS
        db_mock.table.assert_called_once_with("ui_sections")

        # Assert where clause uses the class name for filtering
        expected_name = WidgetController.__name__
        db_table_mock.where.assert_called_once_with("controller = ?", expected_name)
        db_table_mock.order_by.assert_called_once_with("order_id")
        db_table_mock.retrieve.assert_called_once()

        # Assert section storage
        assert controller.sections.rows is not None

    def test_state_management(self, _widget_manager):
        """
        Test the basic dynamic state management methods.
        """

        from savegem.app.gui.controller import WidgetController

        mock_controller = WidgetController(_widget_manager)

        # 1. Test initial state
        assert mock_controller._get_state("key_1") is None

        # 2. Test set and get
        mock_controller._set_state("key_1", 42)
        assert mock_controller._get_state("key_1") == 42

        # 3. Test reset_state
        mock_controller.reset_state()
        assert mock_controller._get_state("key_1") is None

    def test_manager_property(self, _widget_manager):
        """
        Test the manager property getter.
        """

        from savegem.app.gui.controller import WidgetController

        mock_controller = WidgetController(_widget_manager)
        assert mock_controller.manager == _widget_manager

    def test_change_widget_parent(self, mocker: MockerFixture, _widget_manager):
        """
        Tests the _change_widget_parent helper method delegates layout manipulation
        correctly to move a widget.
        """

        from savegem.app.gui.controller import WidgetController

        mock_controller = WidgetController(_widget_manager)

        # Original Widget (The one being moved)
        original_widget = mocker.MagicMock()
        original_widget.metadata.name = "section_A.widget_to_move"
        original_widget.layout.return_value = MagicMock()
        original_layout = original_widget.layout.return_value

        # Target Widget (The new parent)
        target_widget = mocker.MagicMock()
        target_widget.metadata.name = "section_B.new_parent"
        target_widget.layout.return_value = MagicMock()
        target_layout = target_widget.layout.return_value

        # Configure the WidgetManager to return the target widget
        mock_controller.manager.get_widget.return_value = target_widget

        mock_controller._change_widget_parent(original_widget, "section_B", "new_parent")


        mock_controller.manager.get_widget.assert_called_once_with("section_B", "new_parent")
        original_layout.removeWidget.assert_called_once_with(original_widget)
        target_layout.addWidget.assert_called_once_with(original_widget)

    def test_do_work(self, mocker: MockerFixture, _widget_manager, logger_mock, exec_in_block_thread_mock,
                     qthread_mock):
        """
        Tests the _do_work helper method initiates worker1 execution in a blocking thread.
        """

        from savegem.app.gui.controller import WidgetController

        mock_controller = WidgetController(_widget_manager)

        worker = mocker.MagicMock()
        worker.__class__.__name__ = "MyBackgroundWorker"  # Set explicit worker1 name

        mock_controller._do_work(worker)


        qthread_mock.assert_called_once()
        assert mock_controller._WidgetController__thread is qthread_mock.return_value  # noqa
        assert mock_controller._WidgetController__worker == worker  # noqa

        exec_in_block_thread_mock.assert_called_once_with(
            qthread_mock.return_value,  # The newly created thread
            worker  # The worker1 instance
        )

        logger_mock.debug.assert_any_call(
            "Starting %s worker1 from controller %s",
            "MyBackgroundWorker",
            "WidgetController"
        )


class TestTemplateResolver:

    def test_resolve_should_happen_in_controller(self, mocker: MockerFixture):

        from savegem.app.gui.controller import TemplateResolver

        test_value = "test"
        test_args = [1, 2, 432]
        test_kw = {"a": 1, "b": "c"}

        test_element = mocker.MagicMock()
        template_controller = mocker.MagicMock()
        template_resolver = TemplateResolver(template_controller, test_element)

        template_resolver.resolve(test_value, *test_args, **test_kw)

        template_controller.resolve.assert_called_once_with(
            test_element, test_value, *test_args, **test_kw
        )


class TestTemplateWidgetController:

    @pytest.fixture
    def _manager(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _template_controller(self, _manager):
        from savegem.app.gui.controller import TemplateWidgetController
        return TemplateWidgetController(_manager)

    @pytest.fixture
    def _create_widget_meta(self, mocker: MockerFixture):
        def create_widget_meta(widget_id: str, section_id: str, parent_widget_id: str = None, order_id: int = 1):
            widget = mocker.MagicMock()
            widget.id = widget_id
            widget.original_id = widget_id
            widget.section_id = section_id
            widget.parent_widget_id = parent_widget_id
            widget.parent = None
            widget.order_id = order_id

            return widget

        return create_widget_meta

    def test_init_handler_mapping(self, mocker: MockerFixture, get_methods_mock, _manager):
        """
        Test if handlers are correctly discovered and mapped during initialization.
        """

        from savegem.app.gui.controller import TemplateWidgetController

        # Define mock methods to be 'discovered' by get_methods
        widget_a = "widget_a"
        widget_b = "widget_b"
        mock_handler_1 = mocker.MagicMock()
        mock_handler_2 = mocker.MagicMock()

        get_methods_mock.return_value = [
            (f"{TemplateWidgetController.HandlerPrefix}{widget_a}", mock_handler_1),
            (f"{TemplateWidgetController.HandlerPrefix}{widget_b}", mock_handler_2)
        ]

        controller = TemplateWidgetController(_manager)
        handlers = controller._TemplateWidgetController__handlers  # noqa

        assert widget_a in handlers
        assert widget_b in handlers

        assert mock_handler_1 == handlers[widget_a]
        assert mock_handler_2 == handlers[widget_b]
        assert len(handlers) == 2

    def test_refresh_full_cycle(self, mocker: MockerFixture, module_patch, _template_controller, _create_widget_meta,
                                _manager):
        """
        Test the main 'refresh' method, ensuring correct build, delete, and handler invocation.
        """

        def patch_controller(method_name: str):
            if method_name.startswith("__"):
                method_name = "_TemplateWidgetController" + method_name

            return mocker.patch.object(_template_controller, method_name)

        get_data_mock = patch_controller("_get_data")
        segment_meta_mock = patch_controller("__segment_metadata")
        get_segment_root_mock = patch_controller("__get_segment_root")
        invoke_handlers_mock = patch_controller("__invoke_widget_handlers")
        template_resolver_mock = module_patch("TemplateResolver")

        # 1. Setup Input Data
        input_widget_id = "my_template"
        header_section = f"{input_widget_id}__template_header"
        body_section = f"{input_widget_id}__template_body"
        footer_section = f"{input_widget_id}__template_footer"
        dataset = [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'}
        ]

        mock_segment_root_w1 = mocker.MagicMock()
        mock_segment_root_w2 = mocker.MagicMock()

        input_widget = mocker.MagicMock()
        input_widget.metadata = _create_widget_meta(input_widget_id, "main_section")

        header_widget = _create_widget_meta("h1", header_section)
        body_widget_root = _create_widget_meta("b_root", body_section)
        body_widget_child = _create_widget_meta("b_child", footer_section, "b_root", 2)
        footer_widget = _create_widget_meta("f1", f"{input_widget_id}__template_footer")

        header_meta = [header_widget]
        body_meta = [body_widget_root, body_widget_child]
        footer_meta = [footer_widget]

        get_segment_root_mock.side_effect = lambda target, _: target
        get_data_mock.return_value = dataset
        segment_meta_mock.side_effect = [
            {header_widget: header_meta},
            {body_widget_root: body_meta},
            {footer_widget: footer_meta}
        ]
        # Mock get_widget return for handler invocation
        _manager.get_widget.side_effect = [mock_segment_root_w1, mock_segment_root_w2]

        _template_controller.refresh(input_widget)

        segment_meta_mock.assert_has_calls([
            call(header_section, input_widget),
            call(body_section, input_widget),
            call(footer_section, input_widget)
        ])

        _manager.delete.assert_called_once()
        widget_filter = _manager.delete.call_args[0][0]
        non_related_widget = _create_widget_meta("any", "other_section")

        # Verify that widget filter is correct.
        assert widget_filter(header_widget) is True
        assert widget_filter(non_related_widget) is False

        _manager.build.assert_any_call(header_meta)
        _manager.build.assert_any_call(body_meta)
        _manager.build.assert_any_call(footer_meta)

        # Check metadata modification for the first element (idx=0)
        # The body metadata is grouped: {body_meta_root: [body_meta_root, body_meta_child]}

        # Expected ID and order for element 0 (idx=0, widget_count=2):
        # b_root becomes b_root__0, order 0 * 0 + 0 = 0
        # b_child becomes b_child__0, order 0 * 0 + 0 = 0

        # Since deepcopy is called, we check the modified copies passed to build:
        # Check call for element 0 (b_root__0, b_child__0)

        header_build_call = _manager.build.call_args_list[0][0][0]
        assert header_build_call[0].id == "h1"
        assert header_build_call[0].order_id == 1

        body_build_metadata = _manager.build.call_args_list[1][0][0]
        body_root = next(meta for meta in body_build_metadata if meta.original_id == body_widget_root.original_id)
        body_child = next(meta for meta in body_build_metadata if meta.original_id == body_widget_child.original_id)
        assert body_root.id == "b_root__0"
        assert body_root.order_id == 1
        assert body_child.id == "b_child__0"
        assert body_child.order_id == 2

        body_build_metadata = _manager.build.call_args_list[2][0][0]
        body_root = next(meta for meta in body_build_metadata if meta.original_id == body_widget_root.original_id)
        body_child = next(meta for meta in body_build_metadata if meta.original_id == body_widget_child.original_id)
        assert body_root.id == "b_root__1"
        assert body_root.order_id == 3
        assert body_child.id == "b_child__1"
        assert body_child.order_id == 4

        footer_build_call = _manager.build.call_args_list[3][0][0]
        assert footer_build_call[0].id == "f1"
        assert footer_build_call[0].order_id == 1

        # Assert Resolver and Handler Invocation
        assert template_resolver_mock.call_count == 2
        template_resolver_mock.assert_has_calls([
            call(_template_controller, dataset[0]),
            call(_template_controller, dataset[1])
        ])

        assert invoke_handlers_mock.call_count == 2
        invoke_handlers_mock.assert_has_calls([
            call(mock_segment_root_w1, dataset[0]),
            call(mock_segment_root_w2, dataset[1]),
        ])

    def test_resolve_method(self, _template_controller):
        """
        Test the simple resolve method.
        """

        element = {'key': 'value'}
        value = "TOKEN_VALUE"

        result = _template_controller.resolve(element, value, 1, kwarg='test')

        # By default, it just returns the value
        assert result == value

    def test_get_data(self, _template_controller):
        assert len(_template_controller._get_data()) == 0

    def test_invoke_widget_handlers_no_handlers(self, mocker: MockerFixture, _template_controller, _create_widget_meta):
        """
        Test __invoke_widget_handlers when no handlers are defined.
        """

        root_handler = mocker.MagicMock()
        child_handler = mocker.MagicMock()
        _template_controller.handle__root = root_handler
        _template_controller.handle__child_1 = child_handler

        root_widget = mocker.MagicMock()
        root_widget.metadata = _create_widget_meta("root", "section")

        child_widget = mocker.MagicMock()
        child_widget.metadata = _create_widget_meta(
            "child_1", "section", "root", 2
        )
        root_widget.findChildren.return_value = [child_widget]

        # Ensure no handlers exist in the controller's private dictionary
        _template_controller._TemplateWidgetController__handlers = {}

        element = {'data': 1}

        # The method should run without error
        _template_controller._TemplateWidgetController__invoke_widget_handlers(root_widget, element)  # noqa

        root_handler.assert_not_called()
        child_handler.assert_not_called()

    def test_invoke_widget_handlers_with_handlers(self, mocker: MockerFixture, _template_controller,
                                                  _create_widget_meta):
        """
        Test __invoke_widget_handlers when handlers are present and correctly called.
        """

        # 1. Setup Handlers
        mock_handler_for_root = mocker.MagicMock()
        mock_handler_for_child = mocker.MagicMock()

        _template_controller._TemplateWidgetController__handlers = {
            'root': mock_handler_for_root,
            'child': mock_handler_for_child
        }

        # 2. Setup Widgets
        # Root widget (metadata.original_id='root_widget_id')
        root_widget = mocker.MagicMock()
        root_widget.metadata = _create_widget_meta("root__0", "section")
        root_widget.metadata.original_id = "root"

        child_widget = mocker.MagicMock()
        child_widget.metadata = _create_widget_meta("child__0", "section")
        child_widget.metadata.original_id = "child"

        unhandled_widget = mocker.MagicMock()
        unhandled_widget.metadata = _create_widget_meta("unhandled__0", "section")
        unhandled_widget.metadata.original_id = "unhandled"

        root_widget.findChildren.return_value = [child_widget, unhandled_widget]
        element = {'data': 'test_data'}

        # 3. Execute
        _template_controller._TemplateWidgetController__invoke_widget_handlers(root_widget, element)  # noqa

        # 4. Assertions
        mock_handler_for_root.assert_called_once_with(root_widget, element)
        mock_handler_for_child.assert_called_once_with(child_widget, element)

    def test_segment_metadata(self, mocker: MockerFixture, _create_widget_meta, _template_controller):

        test_widget = mocker.MagicMock()
        test_section = "section"

        first_root = _create_widget_meta("root_1", test_section)
        fr_first_child = _create_widget_meta("root_1_child_1", test_section, parent_widget_id="root_1")
        fr_second_child = _create_widget_meta("root_1_child_2", test_section, parent_widget_id="root_1_child_1")

        second_root = _create_widget_meta("root_2", test_section)
        sr_first_child = _create_widget_meta("root_2_child_1", test_section, parent_widget_id="root_2")

        retrieve_meta_mock = mocker.patch.object(WidgetSectionBuildCommand, "retrieve_metadata")
        retrieve_meta_mock.return_value = [
            first_root,
            second_root,
            fr_first_child,
            sr_first_child,
            fr_second_child
        ]

        meta: dict = _template_controller._TemplateWidgetController__segment_metadata(test_section, test_widget)  # noqa

        retrieve_meta_mock.assert_called_once_with(test_section)
        first_segment_meta = meta.get(first_root)
        second_segment_meta = meta.get(second_root)

        # Should be for each segment root.
        assert len(meta) == 2

        assert first_root in first_segment_meta
        assert fr_first_child in first_segment_meta
        assert fr_second_child in first_segment_meta
        assert second_root not in first_segment_meta
        assert sr_first_child not in first_segment_meta

        assert first_root not in second_segment_meta
        assert fr_first_child not in second_segment_meta
        assert fr_second_child not in second_segment_meta
        assert second_root in second_segment_meta
        assert sr_first_child in second_segment_meta
