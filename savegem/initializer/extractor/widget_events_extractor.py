from savegem.initializer.extractor import RegularExtractor


class WidgetEventsExtractor(RegularExtractor):
    """
    Extractor for ui_widget_events table.
    """

    def _post_extract(self, data: list[dict]):

        formatted_data = {}

        for record in data:

            section_id = record.get("section_id")
            widget_id = record.get("widget_id")
            event = record.get("refresh_event_id")
            widget_name = f"{section_id}.{widget_id}"

            events = formatted_data.get(widget_name, [])
            events.append(event)

            formatted_data[widget_name] = events

        return formatted_data
