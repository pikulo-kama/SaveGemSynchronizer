from unittest.mock import call


class TestWidgetsExtractor:

    def test_widget_import(self, db_mock, db_table_mock):

        from src.savegem import WidgetsExtractor

        data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "KWidget",
                "layout_type_id": "KVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
            },
            {
                "widget_id": "app_logo",
                "section_id": "wait",
                "content": "pixmap{gem_outline.svg, scale: 80}",
                'order_id': 1,
                'parent_widget_id': 'wait_bar_root',
                "widget_type_id": "KLabel",
                "alignment": "center"
            },
            {
                "widget_id": "wait_bar",
                "section_id": "wait",
                'order_id': 2,
                'parent_widget_id': 'wait_bar_root',
                "widget_type_id": "QWaitBar",
                "alignment": "bottom",
                "height": 10,
                'stylesheet': '{\n    "background-color": "red",\n    "font-size": "18px"\n}',
            }
        ]

        expected_data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "KWidget",
                "layout_type_id": "KVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
                "children": [
                    {
                        "widget_id": "app_logo",
                        "content": "pixmap{gem_outline.svg, scale: 80}",
                        "widget_type_id": "KLabel",
                        "alignment": "center"
                    },
                    {
                        "widget_id": "wait_bar",
                        "widget_type_id": "QWaitBar",
                        "alignment": "bottom",
                        "height": 10,
                        "stylesheet": {
                            "background-color": "red",
                            "font-size": "18px"
                        }
                    }
                ]
            }
        ]

        extractor = WidgetsExtractor()
        formatted_data = extractor._post_extract(data)

        db_table_mock.where.assert_has_calls([
            call("section_id = ? and widget_id = ?", "wait", "wait_bar_root"),
            call("section_id = ? and widget_id = ?", "wait", "app_logo"),
            call("section_id = ? and widget_id = ?", "wait", "wait_bar")
        ])

        assert formatted_data == expected_data


    def test_should_build_where_clause_correctly_when_section_id_is_null(self, db_table_mock):

        from src.savegem import WidgetsExtractor

        data = [
            {
                "widget_id": "wait_bar_root",
                "widget_type_id": "KWidget",
                "layout_type_id": "KVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
            }
        ]

        extractor = WidgetsExtractor()
        extractor._post_extract(data)

        db_table_mock.where.assert_has_calls([
            call("section_id IS NULL and widget_id = ?", "wait_bar_root")
        ])


    def test_should_include_events_when_extracting(self, db_table_mock):

        from src.savegem import WidgetsExtractor
        from src.savegem import DatabaseRow

        table_columns = ["refresh_event_id", "refresh_children"]
        first_event = "test_event"
        second_event = "another_event"
        third_event = "one_more"

        data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "KWidget",
                "layout_type_id": "KVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
            }
        ]

        expected_data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "KWidget",
                "layout_type_id": "KVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
                "refresh_events": [
                    first_event,
                    second_event
                ],
                "recursive_refresh_events": [
                    third_event
                ]
            }
        ]

        db_table_mock.retrieve.return_value = [
            DatabaseRow(1, (first_event, 0), table_columns),
            DatabaseRow(2, (second_event, 0), table_columns),
            DatabaseRow(3, (third_event, 1), table_columns)
        ]

        extractor = WidgetsExtractor()
        formatted_data = extractor._post_extract(data)

        assert formatted_data == expected_data
