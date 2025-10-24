from savegem.initializer.importer import DatabaseImporter


class TRImporter(DatabaseImporter):
    """
    Importer for text_resources table.
    """

    def _format_data(self, data: dict[dict]):

        resources = []

        for resource_key, resource_data in data.items():
            for locale_id, resource_value in resource_data.items():

                resources.append({
                    "text_resource_key": resource_key,
                    "locale_id": locale_id,
                    "text_resource": resource_value
                })

        return resources
