from unittest.mock import ANY, MagicMock

import pytest
from pytest_mock import MockerFixture


class TestWidgetBuildCommand:

    def test_execute(self, mocker: MockerFixture):

        from src.savegem import WidgetBuildCommand
        from src.savegem import ManagerContext

        build_widget_mock = mocker.patch.object(WidgetBuildCommand, "_build_widget")
        manager = mocker.MagicMock()
        widget1 = mocker.MagicMock()
        widget2 = mocker.MagicMock()

        build_widget_mock.side_effect = [widget1, widget2]

        context = ManagerContext(manager, [], {})
        command = WidgetBuildCommand([widget1.metadata, widget2.metadata])

        command.execute(context)

        assert len(context.new_widgets) == 2
        assert widget1 in context.new_widgets
        assert widget2 in context.new_widgets


    def test_build_widget(self, mocker: MockerFixture, resolve_content_mock):

        from src.savegem import WidgetBuildCommand

        widget = mocker.MagicMock()
        layout = mocker.MagicMock()

        mock_widget_type = mocker.MagicMock()
        mock_widget_type.type.return_value = widget

        mock_layout_type = mocker.MagicMock()
        mock_layout_type.type.return_value = layout

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
        resolve_content_mock.side_effect = lambda c, **kw: f"RESOLVED({c})"

        widget: MagicMock = WidgetBuildCommand._build_widget(meta)  # noqa

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


class TestWidgetSectionBuildCommand:

    @pytest.fixture
    def _meta_from_row_mock(self, module_patch):
        return module_patch("WidgetMetadata.from_database_row")

    def test_controller(self, module_patch):

        from src.savegem import WidgetSectionBuildCommand

        test_section_id = "section"
        base_init_mock = module_patch("WidgetBuildCommand.__init__")
        retrieve_metadata_mock = module_patch("WidgetSectionBuildCommand.retrieve_metadata")

        WidgetSectionBuildCommand(test_section_id)

        base_init_mock.assert_called_once_with(retrieve_metadata_mock.return_value)
        retrieve_metadata_mock.assert_called_once_with(test_section_id)

    @pytest.mark.parametrize("section, where_clause_args", [
        ("root", ["section_id IS NULL"]),
        ("test", ["section_id = ?", "test"])
    ])
    def test_retrieve_with_root_section(self, mocker: MockerFixture, db_mock, db_table_mock, _meta_from_row_mock,
                                        section, where_clause_args):

        from src.savegem import WidgetSectionBuildCommand

        db_table_mock.retrieve.return_value = [
            mocker.MagicMock(),
            mocker.MagicMock()
        ]

        metadata = WidgetSectionBuildCommand.retrieve_metadata(section)

        db_mock.table.assert_called_once_with("ui_widgets")
        db_table_mock.where.assert_called_once_with(*where_clause_args)
        db_table_mock.retrieve.assert_called_once()

        assert _meta_from_row_mock.call_count == 2
        assert len(metadata) == 2
