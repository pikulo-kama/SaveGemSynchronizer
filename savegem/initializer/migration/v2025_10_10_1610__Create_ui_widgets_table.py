from sqlite3 import Connection
from savegem.initializer.migration import Migration


class v2025_10_10_1610__Create_ui_widgets_table(Migration):  # noqa

    def _migrate(self, connection: Connection):
        # Add UI Widgets table.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ui_widgets (
                widget_id VARCHAR NOT NULL,
                section_id VARCHAR,
                content VARCHAR,
                tooltip VARCHAR,
                controller VARCHAR,
                parent_widget_id VARCHAR,
                widget_type_id VARCHAR NOT NULL,
                layout_type_id VARCHAR,
                style_object_name VARCHAR,
                alignment VARCHAR,
                spacing INTEGER,
                width INTEGER,
                height INTEGER,
                margin_left INTEGER,
                margin_top INTEGER,
                margin_right INTEGER,
                margin_bottom INTEGER,
                order_id INTEGER,
                properties TEXT,
                stylesheet TEXT,
                
                PRIMARY KEY (widget_id, section_id),
                FOREIGN KEY (section_id) REFERENCES ui_sections(section_id) 
                    ON DELETE CASCADE
            )
        """)

        # Create table to store refresh events that should trigger refresh of widget.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ui_widget_events (
                widget_id VARCHAR NOT NULL,
                section_id VARCHAR NOT NULL,
                refresh_event_id VARCHAR NOT NULL,
                refresh_children INTEGER DEFAULT 0,
                
                PRIMARY KEY (widget_id, section_id, refresh_event_id),
                FOREIGN KEY (widget_id, section_id) REFERENCES ui_widgets(widget_id, section_id) ON DELETE CASCADE
            )
        """)
