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

    def test_template_import(self, db_table_mock):

        from savegem.initializer.importer.widgets_importer import WidgetsImporter

        data = [
            {
                "widget_id": "game_list",
                "controller": "GameListController",
                "section_id": "test",
                "widget_type_id": "QScrollableWidget",
                "layout_type_id": "QVBoxLayout",
                "template": {
                    "header": [
                        {
                            "widget_id": "header_1",
                            "widget_type_id": "QVBoxLayout",
                            "children": [
                                {
                                    "widget_id": "header_1_1",
                                    "widget_type_id": "QLabel"
                                },
                                {
                                    "widget_id": "header_1_2",
                                    "widget_type_id": "QLabel"
                                }
                            ]
                        },
                        {
                            "widget_id": "header_2",
                            "widget_type_id": "QSpacer"
                        }
                    ],
                    "body": [
                        {
                            "widget_id": "body_1",
                            "widget_type_id": "QHDivider"
                        },
                        {
                            "widget_id": "body_2",
                            "content": "template{name}",
                            "widget_type_id": "QPushButton",
                            "style_object_name": "gameListOption"
                        }
                    ],
                    "footer": [
                        {
                            "widget_id": "footer_1",
                            "widget_type_id": "QVBoxLayout",
                            "children": [
                                {
                                    "widget_id": "footer_1_1",
                                    "widget_type_id": "QLabel"
                                },
                                {
                                    "widget_id": "footer_1_2",
                                    "widget_type_id": "QLabel"
                                }
                            ]
                        },
                        {
                            "widget_id": "footer_2",
                            "widget_type_id": "QSpacer"
                        }
                    ]
                }
            }
        ]

        expected_data = [
            # Root widget imported first.
            {
                "controller": "GameListController",
                "layout_type_id": "QVBoxLayout",
                "section_id": "test",
                "widget_id": "game_list",
                "widget_type_id": "QScrollableWidget"
            },
            # Then header widgets.
            {
                "order_id": 1,
                "section_id": "game_list__template_header",
                "widget_id": "header_1",
                "widget_type_id": "QVBoxLayout"
            },
            # Then children of root widgets.
            {
                "order_id": 1,
                "parent_widget_id": "header_1",
                "section_id": "game_list__template_header",
                "widget_id": "header_1_1",
                "widget_type_id": "QLabel"
            },
            {
                "order_id": 2,
                "parent_widget_id": "header_1",
                "section_id": "game_list__template_header",
                "widget_id": "header_1_2",
                "widget_type_id": "QLabel"
            },
            # Second header root widget.
            {
                "order_id": 2,
                "section_id": "game_list__template_header",
                "widget_id": "header_2",
                "widget_type_id": "QSpacer"
            },
            # Body widgets.
            {
                "order_id": 1,
                "section_id": "game_list__template_body",
                "widget_id": "body_1",
                "widget_type_id": "QHDivider"
            },
            {
                "content": "template{name}",
                "order_id": 2,
                "section_id": "game_list__template_body",
                "style_object_name": "gameListOption",
                "widget_id": "body_2",
                "widget_type_id": "QPushButton"
            },
            # Footer widgets.
            {
                "order_id": 1,
                "section_id": "game_list__template_footer",
                "widget_id": "footer_1",
                "widget_type_id": "QVBoxLayout"
            },
            {
                "order_id": 1,
                "parent_widget_id": "footer_1",
                "section_id": "game_list__template_footer",
                "widget_id": "footer_1_1",
                "widget_type_id": "QLabel"
            },
            {
                "order_id": 2,
                "parent_widget_id": "footer_1",
                "section_id": "game_list__template_footer",
                "widget_id": "footer_1_2",
                "widget_type_id": "QLabel"
            },
            {
                "order_id": 2,
                "section_id": "game_list__template_footer",
                "widget_id": "footer_2",
                "widget_type_id": "QSpacer"
            }
        ]

        importer = WidgetsImporter()
        formatted_data = importer._format_data(data, {})

        # Should be called for each root widget
        # of each template section (header, body, footer)
        db_table_mock.where.assert_has_calls([
            call("section_id == 'game_list__template_header'"),
            call("section_id == 'game_list__template_header'"),
            call("section_id == 'game_list__template_body'"),
            call("section_id == 'game_list__template_body'"),
            call("section_id == 'game_list__template_footer'"),
            call("section_id == 'game_list__template_footer'")
        ])

        # 1 for main import of metadata
        # + 6 for each template section's root widget.
        assert db_table_mock.retrieve.call_count == 7
        assert db_table_mock.remove_all.call_count == 7
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
