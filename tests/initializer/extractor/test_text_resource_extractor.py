

class TestTextResourceExtractor:

    def test_text_resource_import(self):

        from src.savegem import TextResourceExtractor

        data = [
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

        expected_data = {
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

        extractor = TextResourceExtractor()
        formatted_data = extractor._post_extract(data)

        assert formatted_data == expected_data
