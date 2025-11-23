import json

from savegem.common.db.manager import db
from savegem.initializer.importer import RegularImporter


class WidgetsImporter(RegularImporter):
    """
    Importer for ui_widgets table.
    """

    def _format_data(self, data: list[dict], metadata: dict):
        formatted_data = []
        filter_string = metadata.get("filter")

        events_table = db().table("ui_widget_events")

        if filter_string:
            events_table.where(filter_string)

        # Remove widget events before importing.
        events_table.retrieve()
        events_table.remove_all()
        events_table.save()

        for root_widget in data:
            for widget in self.__flatten_tree(root_widget, root_widget, events_table):
                formatted_data.append(widget)

        return formatted_data

    def __flatten_tree(self, root_widget, parent, events_table):
        """
        Used to go through widget tree
        and format it back into flat structure.
        """

        widgets = []

        parent["section_id"] = root_widget.get("section_id")
        children = parent.get("children", [])
        refresh_events = parent.get("refresh_events", [])
        recursive_refresh_events = parent.get("recursive_refresh_events", [])
        all_events = refresh_events + recursive_refresh_events

        # Save refresh events.
        for event in all_events:
            refresh_children = 1 if event in recursive_refresh_events else 0
            row = events_table.add_row()

            events_table.set(row, "section_id", parent["section_id"])
            events_table.set(row, "widget_id", parent["widget_id"])
            events_table.set(row, "refresh_event_id", event)
            events_table.set(row, "refresh_children", refresh_children)

        events_table.save()

        if "stylesheet" in parent:
            parent["stylesheet"] = json.dumps(parent.get("stylesheet"), indent=4)

        if "refresh_events" in parent:
            del parent["refresh_events"]

        if "recursive_refresh_events" in parent:
            del parent["recursive_refresh_events"]

        if "children" in parent:
            del parent["children"]

        widgets.append(parent)

        order = 0
        for widget in children:
            order += 1
            widget["order_id"] = order
            widget["parent_widget_id"] = parent["widget_id"]

            for child_widget in self.__flatten_tree(root_widget, widget, events_table):
                widgets.append(child_widget)

        return widgets
