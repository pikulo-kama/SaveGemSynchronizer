

class TestTextResourceImporter:

    def test_tr_importer(self):

        from src.savegem import TextResourceImporter

        data = {
            "label_Test": {
                "en": "1",
                "uk": "2"
            },
            "label_AnotherTest": {
                "en": "a",
                "uk": "b",
                "fr": "c"
            }
        }

        expected_data = [
            {
                "text_resource_key": "label_Test",
                "locale_id": "en",
                "text_resource": "1"
            },
            {
                "text_resource_key": "label_Test",
                "locale_id": "uk",
                "text_resource": "2"
            },
            {
                "text_resource_key": "label_AnotherTest",
                "locale_id": "en",
                "text_resource": "a"
            },
            {
                "text_resource_key": "label_AnotherTest",
                "locale_id": "uk",
                "text_resource": "b"
            },
            {
                "text_resource_key": "label_AnotherTest",
                "locale_id": "fr",
                "text_resource": "c"
            }
        ]

        importer = TextResourceImporter()
        formatted_data = importer._format_data(data, {})

        assert formatted_data == expected_data
