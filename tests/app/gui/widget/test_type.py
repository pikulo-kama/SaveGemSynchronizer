import pytest
from pytest_mock import MockerFixture




class DummyWidget: pass
DUMMY_CLASS_PATH = f'{__name__}.DummyWidget'


class WidgetTypeTestModuleHelper:

    @pytest.fixture(autouse=True)
    def _setup(self, mocker: MockerFixture):
        """
        Resets the global state lists before each test runs to ensure singleton logic is testable.
        """

        import savegem.app.gui.widget.type as type_module

        mocker.patch.object(type_module, '_widget_type_pool', new=[])
        mocker.patch.object(type_module, '_layout_type_pool', new=[])


class TestCoreUtilities(WidgetTypeTestModuleHelper):

    def test_ui_object_type_properties(self, importlib_mock):
        """
        Test the basic getters of UIObjectType.
        """

        from savegem.app.gui.widget.type import UIObjectType

        obj = UIObjectType("Label", str)
        assert obj.name == "Label"
        assert obj.type == str

    def test_widget_type_properties(self, importlib_mock):
        """
        Test the additional property of WidgetType.
        """

        from savegem.app.gui.widget.type import WidgetType

        widget = WidgetType("Button", int, is_interactable=True)
        assert widget.name == "Button"
        assert widget.type == int
        assert widget.is_interactable is True

        widget_non_interactable = WidgetType("Image", float, is_interactable=False)
        assert widget_non_interactable.is_interactable is False

    def test_get_class_from_path_success(self, importlib_mock, module_patch):
        """
        Test dynamic loading of a class from a string path.
        """

        from savegem.app.gui.widget.type import get_class_from_path

        get_attr_mock = module_patch("getattr")
        get_attr_mock.return_value = DummyWidget

        result_class = get_class_from_path(DUMMY_CLASS_PATH)

        # Verify importlib was called correctly
        importlib_mock.import_module.assert_called_once_with(__name__)
        get_attr_mock.assert_called_once_with(importlib_mock.import_module.return_value, 'DummyWidget')

        assert result_class == DummyWidget

    def test_get_class_from_path_invalid(self):
        """
        Test that failure to load raises an appropriate error.
        """

        from savegem.app.gui.widget.type import get_class_from_path

        with pytest.raises(ImportError):
            get_class_from_path("non.existent.path.InvalidClass")


class TestWidgetTypePool:

    WIDGET_DB_DATA = [
        {
            "widget_type_id": "LBL_NORMAL",
            "class_path": DUMMY_CLASS_PATH,
            "is_interactable": 0
        },
        {
            "widget_type_id": "BTN_PRIMARY",
            "class_path": DUMMY_CLASS_PATH,
            "is_interactable": 1
        }
    ]

    @pytest.fixture
    def _mock_db_load(self, db_mock, importlib_mock):
        """
        Helper to configure DB and import mocks for loading.
        """

        db_mock.retrieve_table.return_value = self.WIDGET_DB_DATA
        importlib_mock.import_module.return_value.DummyWidget = DummyWidget


    def test_pool_lazy_loading_and_singleton(self, db_mock, _mock_db_load):
        """
        Tests that the DB is called only once to load the pool.
        """

        from savegem.app.gui.widget.type import _get_widget_type_pool

        # 1. First call loads the data
        pool_1 = _get_widget_type_pool()

        # 2. Second call should hit the cache, not the DB
        pool_2 = _get_widget_type_pool()

        # Assert DB was called only once
        db_mock.retrieve_table.assert_called_once_with("setup_widget_type")

        # Assert the same list is returned
        assert pool_1 is pool_2
        assert len(pool_1) == 2

        # Check correct mapping of interactable flag
        assert pool_1[0].name == "LBL_NORMAL"
        assert pool_1[0].is_interactable is False
        assert pool_1[1].is_interactable is True


    def test_get_widget_type_by_name(self, _mock_db_load):
        """
        Test lookup by widget type ID.
        """

        from savegem.app.gui.widget.type import get_widget_type

        widget_type = get_widget_type("BTN_PRIMARY")

        assert widget_type.name == "BTN_PRIMARY"
        assert widget_type.type == DummyWidget
        assert widget_type.is_interactable is True

        # Test failure case
        with pytest.raises(StopIteration):
            get_widget_type("NON_EXISTENT")


    def test_get_widget_type_by_class(self, db_mock, _mock_db_load):
        """
        Test lookup by the loaded class object.
        """

        from savegem.app.gui.widget.type import get_widget_type_by_class

        widget_type = get_widget_type_by_class(DummyWidget)

        assert widget_type.name == "LBL_NORMAL"  # The first one found with DummyWidget class
        assert widget_type.type == DummyWidget


class TestLayoutTypePool:

    LAYOUT_DB_DATA = [
        {
            "layout_type_id": "V_LAYOUT",
            "class_path": DUMMY_CLASS_PATH,
        },
        {
            "layout_type_id": "H_LAYOUT",
            "class_path": DUMMY_CLASS_PATH,
        }
    ]

    @pytest.fixture
    def _mock_db_load(self, db_mock, importlib_mock):
        """
        Helper to configure DB and import mocks for loading.
        """

        db_mock.retrieve_table.return_value = self.LAYOUT_DB_DATA
        importlib_mock.import_module.return_value.DummyWidget = DummyWidget


    def test_get_layout_type_loading(self, db_mock, _mock_db_load):
        """
        Tests that the pool loads data from the DB and caches it.
        """

        from savegem.app.gui.widget.type import get_layout_type

        # 1. First call loads the data
        layout_type = get_layout_type("V_LAYOUT")

        # 2. Second call should hit the cache, not the DB
        get_layout_type("H_LAYOUT")

        # Assert DB was called only once
        db_mock.retrieve_table.assert_called_once_with("setup_layout_type")

        # Check correct mapping
        assert layout_type.name == "V_LAYOUT"
        assert layout_type.type == DummyWidget

    def test_get_layout_type_not_found(self, _mock_db_load):
        """
        Test that not finding a layout type returns None.
        """

        from savegem.app.gui.widget.type import get_layout_type

        result = get_layout_type("MISSING")
        assert result is None
