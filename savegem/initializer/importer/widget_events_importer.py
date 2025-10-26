from savegem.initializer.importer import RegularImporter


class WidgetEventsImporter(RegularImporter):
    """
    Importer for ui_widget_events table.
    """

    def _format_data(self, data: dict[str, dict]):
        formatted_data = []

        for widget_name, widget_data in data.items():
            section_id, widget_id = widget_name.split(".")
            refresh_children = widget_data.get("refresh_children")
            events = widget_data.get("events")

            for event in events:
                formatted_data.append({
                    "widget_id": widget_id,
                    "section_id": section_id,
                    "refresh_event_id": event,
                    "refresh_children": 1 if refresh_children else 0
                })

        return formatted_data
