from savegem.initializer.extractor import RegularExtractor


class WidgetEventsExtractor(RegularExtractor):
    """
    Extractor for ui_widget_events table.
    """

    def _post_extract(self, data: list[dict]):

        formatted_data: dict[str, dict] = {}

        for record in data:

            section_id = record.get("section_id")
            widget_id = record.get("widget_id")
            event = record.get("refresh_event_id")
            widget_name = f"{section_id}.{widget_id}"

            widget_obj = formatted_data.get(widget_name)

            if widget_obj is None:
                widget_obj = {
                    "refresh_children": record.get("refresh_children") == 1,
                    "events": []
                }

                # Only include refresh children flag if it's True.
                if not widget_obj.get("refresh_children"):
                    del widget_obj["refresh_children"]

            events = widget_obj.get("events")
            events.append(event)

            widget_obj["events"] = events
            formatted_data[widget_name] = widget_obj

        return formatted_data
