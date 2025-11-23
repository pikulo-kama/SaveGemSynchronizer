import json

from savegem.common.db.manager import db
from savegem.initializer.extractor import RegularExtractor


class WidgetsExtractor(RegularExtractor):
    """
    Extractor for ui_widgets table.
    """

    def _post_extract(self, data: list[dict]):
        widget_data = self.__build_tree(data)
        return self.__format_tree(widget_data)

    def __build_tree(self, widget_data, parent_id=None):
        """
        Used to recursively collect widgets based on
        parent widget and return a tree structure.
        """

        widgets = []

        for widget in widget_data:
            section_id = widget.get("section_id")
            widget_id = widget.get("widget_id")
            widget_parent_id = widget.get("parent_widget_id")
            widget_unique_id = f"{section_id}.{widget_id}"
            widget_unique_parent_id = f"{section_id}.{widget_parent_id}"

            events = db().table("ui_widget_events") \

            if section_id is None:
                events.where("section_id IS NULL and widget_id = ?", widget_id)
            else:
                events.where("section_id = ? and widget_id = ?", section_id, widget_id)

            refresh_events = []
            recursive_refresh_events = []

            # Collect widget events.
            for event in events.retrieve():
                event_id = event.get("refresh_event_id")
                is_recursive = event.get("refresh_children") == 1

                if is_recursive:
                    recursive_refresh_events.append(event_id)

                else:
                    refresh_events.append(event_id)

            if len(refresh_events) > 0:
                widget["refresh_events"] = refresh_events

            if len(recursive_refresh_events) > 0:
                widget["recursive_refresh_events"] = recursive_refresh_events

            if widget_unique_parent_id == parent_id or (parent_id is None and widget_parent_id is None):
                children = self.__build_tree(widget_data, parent_id=widget_unique_id)
                widget["children"] = children

                widgets.append(widget)

        return widgets

    def __format_tree(self, widget_data):
        """
        Used to recursively go through widget tree
        and cleanup/format some of its properties.
        """

        widget_data.sort(key=lambda w: w.get("order_id", 0))

        for widget in widget_data:

            section_id = widget.get("section_id")
            parent_widget_id = widget.get("parent_widget_id")
            stylesheet = widget.get("stylesheet")

            # Only show section ID on root widgets.
            if parent_widget_id is not None and section_id is not None:
                del widget["section_id"]

            # Remove parent widget id.
            if parent_widget_id is not None:
                del widget["parent_widget_id"]

            # Remove order id.
            if "order_id" in widget:
                del widget["order_id"]

            if stylesheet is not None:
                widget["stylesheet"] = json.loads(stylesheet)

            children = widget.get("children", [])
            formatted_children = self.__format_tree(children)
            widget["children"] = formatted_children

            # No need to show empty children object.
            if len(children) == 0:
                del widget["children"]

        return widget_data
