from unittest.mock import call


class TestWidgetsImporter:

    def test_widgets_import(self, db_table_mock):

        from savegem.initializer.importer.widgets_importer import WidgetsImporter

        data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "QWidget",
                "layout_type_id": "QVBoxLayout",
                "spacing": 30,
                "width": 400,
                "margin_bottom": 50,
                "children": [
                    {
                      "widget_id": "app_logo",
                      "content": "pixmap{gem_outline.svg, scale: 80}",
                      "widget_type_id": "QLabel",
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

        expected_data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "QWidget",
                "layout_type_id": "QVBoxLayout",
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
                "widget_type_id": "QLabel",
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

        importer = WidgetsImporter()
        formatted_data = importer._format_data(data, {})

        db_table_mock.where.assert_not_called()
        db_table_mock.retrieve.assert_called_once()
        db_table_mock.remove_all.assert_called_once()
        db_table_mock.save.call_count = 4  # 1 when removing existing events + 3 for each widget

        assert formatted_data == expected_data


    def test_should_apply_filter_when_provided(self, db_table_mock):

        from savegem.initializer.importer.widgets_importer import WidgetsImporter

        data_filter = "column = 'a'"

        importer = WidgetsImporter()
        importer._format_data([], {"filter": data_filter})

        db_table_mock.where.assert_called_once_with(data_filter)


    def test_should_import_events_when_present(self, db_table_mock):

        from savegem.initializer.importer.widgets_importer import WidgetsImporter

        first_event = "test_event"
        second_event = "another_event"
        third_event = "one_more"

        data = [
            {
                "widget_id": "wait_bar_root",
                "section_id": "wait",
                "widget_type_id": "QWidget",
                "layout_type_id": "QVBoxLayout",
                "refresh_events": [
                    first_event,
                    second_event
                ],
                "recursive_refresh_events": [
                    third_event
                ]
            }
        ]

        db_table_mock.add_row.side_effect = [1, 2, 3]

        importer = WidgetsImporter()
        importer._format_data(data, {})

        db_table_mock.set.assert_has_calls([
            call(1, "section_id", "wait"),
            call(1, "widget_id", "wait_bar_root"),
            call(1, "refresh_event_id", first_event),
            call(1, "refresh_children", 0),

            call(2, "section_id", "wait"),
            call(2, "widget_id", "wait_bar_root"),
            call(2, "refresh_event_id", second_event),
            call(2, "refresh_children", 0),

            call(3, "section_id", "wait"),
            call(3, "widget_id", "wait_bar_root"),
            call(3, "refresh_event_id", third_event),
            call(3, "refresh_children", 1)
        ])
