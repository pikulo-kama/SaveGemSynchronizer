from savegem.initializer.importer import RegularImporter


class WidgetEventsImporter(RegularImporter):
    """
    Importer for ui_widget_events table.
    """

    def _format_data(self, data: dict[str, list[str]]):
        formatted_data = []

        for widget_name, events in data.items():
            section_id, widget_id = widget_name.split(".")

            for event in events:
                formatted_data.append({
                    "widget_id": widget_id,
                    "section_id": section_id,
                    "refresh_event_id": event
                })

        return formatted_data
