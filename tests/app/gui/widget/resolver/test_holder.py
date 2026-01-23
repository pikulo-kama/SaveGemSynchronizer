

class TestDataResolver:

    def test_should_resolve_string_data(self, holder_mock):

        from src.savegem import DataResolver

        holder_mock.get.side_effect = lambda key: {
            "first": "Test123",
            "second": "Test456"
        }.get(key)

        resolver = DataResolver()
        assert resolver.resolve("first") == "Test123"
        assert resolver.resolve("second") == "Test456"

    def test_should_not_resolve_non_string_data(self, holder_mock):

        from src.savegem import DataResolver

        holder_mock.get.side_effect = lambda key: {
            "function": lambda: None,
            "integer": 123,
            "object": {}
        }.get(key)

        resolver = DataResolver()
        assert resolver.resolve("function") is None
        assert resolver.resolve("integer") is None
        assert resolver.resolve("object") is None
