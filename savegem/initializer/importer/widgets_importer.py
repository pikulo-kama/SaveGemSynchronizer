import json
from savegem.initializer.importer import DatabaseImporter


class WidgetsImporter(DatabaseImporter):
    """
    Importer for ui_widgets table.
    """

    def _format_data(self, data: list[dict]):
        formatted_data = []

        for root_widget in data:
            for widget in self.__flatten_tree(root_widget, root_widget):
                formatted_data.append(widget)

        return formatted_data

    def __flatten_tree(self, root_widget, parent):
        """
        Used to go through widget tree
        and format it back into flat structure.
        """

        widgets = []

        parent["section_id"] = root_widget.get("section_id")
        children = parent.get("children", [])

        if "properties" in parent:
            parent["properties"] = json.dumps(parent.get("properties"), indent=4)

        if "stylesheet" in parent:
            parent["stylesheet"] = json.dumps(parent.get("stylesheet"), indent=4)

        if "children" in parent:
            del parent["children"]

        widgets.append(parent)

        order = 0
        for widget in children:
            order += 1
            widget["order_id"] = order
            widget["parent_widget_id"] = parent["widget_id"]

            for child_widget in self.__flatten_tree(root_widget, widget):
                widgets.append(child_widget)

        return widgets
