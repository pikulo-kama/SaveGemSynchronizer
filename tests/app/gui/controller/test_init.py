from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture


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

        from savegem.app.gui.controller import load_controllers

        def _get_members(_, __):
            yield "MockController", _mock_controller

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
        Tests the _do_work helper method initiates worker execution in a blocking thread.
        """

        from savegem.app.gui.controller import WidgetController

        mock_controller = WidgetController(_widget_manager)

        worker = mocker.MagicMock()
        worker.__class__.__name__ = "MyBackgroundWorker"  # Set explicit worker name

        mock_controller._do_work(worker)


        qthread_mock.assert_called_once()
        assert mock_controller._WidgetController__thread is qthread_mock.return_value  # noqa
        assert mock_controller._WidgetController__worker == worker  # noqa

        exec_in_block_thread_mock.assert_called_once_with(
            qthread_mock.return_value,  # The newly created thread
            worker  # The worker instance
        )

        logger_mock.debug.assert_any_call(
            "Starting %s worker from controller %s",
            "MyBackgroundWorker",
            "WidgetController"
        )
