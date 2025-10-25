from savegem.initializer.extractor import DatabaseExtractor


class TRExtractor(DatabaseExtractor):
    """
    Extractor for text_resources table.
    """

    def _get_table_name(self, args):
        return "setup_text_resource"

    def _post_extract(self, data: any):
        formatted_data = {}

        for record in sorted(data, key=lambda r: r.get("text_resource_key")):
            key = record.get("text_resource_key")
            locale = record.get("locale_id")
            value = record.get("text_resource")

            translations = formatted_data.get(key, {})
            translations[locale] = value

            formatted_data[key] = translations

        return formatted_data
