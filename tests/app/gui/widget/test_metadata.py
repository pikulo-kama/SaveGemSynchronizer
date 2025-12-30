import pytest
import json
from PyQt6.QtCore import Qt
from pytest_mock import MockerFixture


class TestRefreshEventMetadata:

    def test_init(self):
        from savegem.app.gui.widget.metadata import RefreshEventMetadata

        meta = RefreshEventMetadata(refresh_children=True)
        assert meta.refresh_children is True

        meta_false = RefreshEventMetadata(refresh_children=False)
        assert meta_false.refresh_children is False


class TestWidgetMetadata:

    @pytest.fixture(autouse=True)
    def _setup(self, module_patch, _create_type_object):
        """
        Mocks all external dependencies used in the file.
        """

        # Mock type resolution functions
        module_patch("get_widget_type", return_value=_create_type_object("MOCK_WIDGET_TYPE"))
        module_patch("get_layout_type", return_value=_create_type_object("MOCK_LAYOUT_TYPE"))

        # Mock style resolution function
        module_patch("resolve_style_properties", side_effect=lambda s: f"RESOLVED({s})")

    @pytest.fixture
    def _init_kw(self, _create_type_object):
        return {
            'widget_id': 'test_id',
            'section_id': 'test_section',
            'widget_type': _create_type_object('Button'),
        }

    @pytest.fixture
    def _create_type_object(self, mocker: MockerFixture):

        def create_type(name: str):
            type_object = mocker.MagicMock()
            type_object.name = name

            return type_object

        return create_type

    @pytest.fixture
    def _mock_widget_events(self, db_table_mock):
        """
        Mocks the database layer to return metadata and event rows.
        """

        from savegem.common.db.table import DatabaseRow

        db_table_mock.retrieve.return_value = [
            DatabaseRow(1, ("LOAD_COMPLETE", 1), ["refresh_event_id", "refresh_children"]),
            DatabaseRow(1, ("DATA_CHANGE", 0), ["refresh_event_id", "refresh_children"])
        ]

    def test_id_setting(self, _init_kw):

        from savegem.app.gui.widget.metadata import WidgetMetadata

        original_id = _init_kw["widget_id"]
        new_id = "new_id"

        meta = WidgetMetadata(**_init_kw)

        assert meta.id == original_id
        assert meta.original_id == original_id

        meta.id = new_id

        assert meta.id == new_id
        assert meta.original_id == original_id

    def test_parent(self, _init_kw):

        from savegem.app.gui.widget.metadata import WidgetMetadata

        original_parent_id = "parent_id"
        new_parent_id = "new_parent_id"
        new_section_id = "new"

        meta = WidgetMetadata(**_init_kw, parent_widget_id=original_parent_id)
        parent_meta = WidgetMetadata(widget_id=new_parent_id, section_id=new_section_id, widget_type=meta.widget_type)

        assert meta.parent is None
        assert meta.parent_widget_id == original_parent_id
        assert meta.parent_widget_name == f"{_init_kw["section_id"]}.{original_parent_id}"

        meta.parent_widget_id = new_parent_id

        assert meta.parent is None
        assert meta.parent_widget_id == new_parent_id
        assert meta.parent_widget_name == f"{_init_kw["section_id"]}.{new_parent_id}"

        meta.parent = parent_meta
        meta.parent.parent_widget_id = original_parent_id

        assert meta.parent == parent_meta
        assert meta.parent_widget_id == "new_parent_id"
        assert meta.parent_widget_name == f"{new_section_id}.{new_parent_id}"

    def test_resolvers(self, _init_kw):

        from savegem.app.gui.widget.metadata import WidgetMetadata
        from savegem.app.gui.widget.resolver import ContentResolver

        class TestResolver1(ContentResolver): pass
        class TestResolver2(ContentResolver): pass

        resolver1 = TestResolver1()
        resolver2 = TestResolver2()

        meta = WidgetMetadata(**_init_kw)

        assert len(meta.resolvers) == 0

        meta.add_resolver(resolver1)

        assert len(meta.resolvers) == 1
        assert meta.resolvers["testresolver1"] == resolver1

        meta.add_resolver(resolver2)

        assert len(meta.resolvers) == 2
        assert meta.resolvers["testresolver1"] == resolver1
        assert meta.resolvers["testresolver2"] == resolver2

    def test_init_defaults(self, _init_kw):
        """
        Test default values and mandatory setup for refresh events.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata, UIRefreshEvent

        meta = WidgetMetadata(**_init_kw)

        # Mandatory refresh event check
        assert UIRefreshEvent.All in meta.refresh_events
        assert len(meta.refresh_events) == 1
        assert meta.should_refresh_children(UIRefreshEvent.All) is False

        # Default numeric values
        assert meta.order_id == 0
        assert meta.margin_left == 0
        assert meta.margin_top == 0
        assert meta.margin_right == 0
        assert meta.margin_bottom == 0

        # Default string/object values
        assert meta.stylesheet == "RESOLVED()"  # Check mock call
        assert meta.alignment == Qt.AlignmentFlag(0)
        assert meta.properties == {}
        assert meta.widget_type is not None
        assert meta.layout_type is None
        assert meta.grid_columns is None
        assert meta.spacing is None
        assert meta.controller is None

    def test_should_allow_changing_order_id(self, _init_kw):

        from savegem.app.gui.widget.metadata import WidgetMetadata

        meta = WidgetMetadata(**_init_kw, order_id=10)
        assert meta.order_id == 10

        meta.order_id = 123
        assert meta.order_id == 123

    def test_complex_init_values(self, _create_type_object):
        """
        Test non-default initialization values and derived properties.
        """

        from savegem.app.gui.widget.metadata import RefreshEventMetadata, WidgetMetadata, UIRefreshEvent

        events_meta = {"CUSTOM_EVENT": RefreshEventMetadata(True)}

        meta = WidgetMetadata(
            widget_id='child',
            section_id='home',
            parent_widget_id='parent',
            widget_type=_create_type_object('Label'),
            stylesheet='color: blue',
            refresh_events=['CUSTOM_EVENT', UIRefreshEvent.All],  # UIRefreshEvent.All is redundant
            refresh_events_meta=events_meta
        )

        # Derived Properties
        assert meta.name == "home.child"
        assert meta.parent_widget_name == "home.parent"
        assert meta.stylesheet == "RESOLVED(color: blue)"

        # Refresh Events (should be unique and include All)
        assert len(meta.refresh_events) == 2
        assert "CUSTOM_EVENT" in meta.refresh_events
        assert UIRefreshEvent.All in meta.refresh_events
        assert meta.should_refresh_children("CUSTOM_EVENT") is True
        assert meta.should_refresh_children(UIRefreshEvent.All) is False
        assert meta.should_refresh_children("INVALID_EVENT") is False

    def test_section_id_root(self, _create_type_object):
        """
        Test section_id logic when it is None.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata, UISection

        meta = WidgetMetadata(
            widget_id='test',
            section_id=None,  # noqa
            widget_type=_create_type_object('Type')
        )

        assert meta.section_id == UISection.RootSection
        assert meta.raw_section_id is None
        assert meta.is_root_section is True
        assert meta.name == f"{UISection.RootSection}.test"


    def test_parse_alignment_single_flag(self):
        """
        Test parsing a single alignment string.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata
        assert WidgetMetadata._WidgetMetadata__parse_alignment("right") == Qt.AlignmentFlag.AlignRight  # noqa


    def test_parse_alignment_multiple_flags(self):
        """
        Test parsing a hyphenated alignment string.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata

        expected = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        assert WidgetMetadata._WidgetMetadata__parse_alignment("top-left") == expected  # noqa

    def test_parse_alignment_none(self):
        """
        Test parsing None returns the default flag.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata
        assert WidgetMetadata._WidgetMetadata__parse_alignment(None) == Qt.AlignmentFlag(0)  # noqa

    def test_parse_stylesheet(self):
        """
        Test converting JSON dict to QSS string.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata

        style_dict = {"color": "red", "padding": "0px"}
        expected_string = "color: red;\npadding: 0px;\n"

        # Use name mangling to access the static method
        result = WidgetMetadata._WidgetMetadata__parse_stylesheet(style_dict)  # noqa
        assert result == expected_string

    @pytest.mark.parametrize("raw_name, expected_name, expected_props", [
        ("buttonName[color=blue]", "buttonName", {"color": "blue"}),
        ("header[align=center, weight=bold]", "header", {"align": "center", "weight": "bold"}),
        ("noProps", "noProps", {}),
        ("[onlyProps=true]", None, {"onlyProps": None}),  # This case is unlikely based on the regex but testing boundary
        (None, None, {})
    ])
    def test_parse_style_object_name(self, _init_kw, raw_name, expected_name, expected_props):
        """
        Tests parsing object name and properties from the composed string.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata

        meta = WidgetMetadata(**_init_kw)

        # Access the private method via name mangling
        meta._WidgetMetadata__parse_style_object_name(raw_name)  # noqa

        assert meta.object_name == expected_name

        if expected_props:
            for key, value in expected_props.items():
                if value is not None:
                    assert meta.properties.get(key) == value


    def test_from_database_row_success(self, _mock_widget_events, db_table_mock):
        """
        Test successful mapping of a typical database row.
        """

        from savegem.app.gui.widget.metadata import WidgetMetadata, UIRefreshEvent
        from savegem.common.db.table import DatabaseRow

        input_data = {
            "widget_id": "main_view",
            "section_id": "root",
            "widget_type_id": "KCustomWidget",
            "layout_type_id": "KCustomVBoxLayout",
            "parent_widget_id": None,
            "controller": "MainController",
            "order_id": 1,
            "grid_columns": 2,
            "spacing": 5,
            "width": 500,
            "height": 400,
            "margin_left": 10,
            "margin_top": 20,
            "margin_right": 30,
            "margin_bottom": 40,
            "style_object_name": "rootWidget[color=white]",
            "content": "Application Title",
            "tooltip": "Main window",
            "alignment": "top-left",
            "stylesheet": json.dumps({"background": "black"})
        }

        metadata_row = DatabaseRow(1, tuple(input_data.values()), list(input_data.keys()))

        meta = WidgetMetadata.from_database_row(metadata_row)

        # ASSERT LOOKUP (DB events table query)
        db_table_mock.where.assert_called_once_with("widget_id = ? AND section_id = ?", "main_view", "root")

        # ASSERT PROPERTIES
        assert meta.id == "main_view"
        assert meta.section_id == "root"
        assert meta.controller == "MainController"
        assert meta.content == "Application Title"
        assert meta.tooltip == "Main window"
        assert meta.width == 500
        assert meta.height == 400
        assert meta.alignment == (Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        assert meta.object_name == "rootWidget"
        assert meta.properties.get("color") == "white"
        assert meta.stylesheet == "RESOLVED(background: black;\n)"

        # ASSERT EVENTS
        assert "LOAD_COMPLETE" in meta.refresh_events
        assert meta.should_refresh_children("LOAD_COMPLETE") is True
        assert meta.should_refresh_children("DATA_CHANGE") is False
        assert meta.should_refresh_children(UIRefreshEvent.All) is False


    def test_widget_without_section_id(self, db_table_mock):

        from savegem.app.gui.widget.metadata import WidgetMetadata
        from savegem.common.db.table import DatabaseRow

        row = DatabaseRow(1, ("id", None), ["widget_id", "section_id"])
        WidgetMetadata.from_database_row(row)

        db_table_mock.where.assert_called_once_with("widget_id = ? AND section_id IS NULL", "id")
