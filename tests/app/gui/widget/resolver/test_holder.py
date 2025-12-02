

class TestDataResolver:

    def test_should_resolve_string_data(self, holder_mock):

        from savegem.app.gui.widget.resolver.holder import DataResolver

        holder_mock.get.side_effect = lambda key: {
            "first": "Test123",
            "second": "Test456"
        }.get(key)

        resolver = DataResolver()
        assert resolver.resolve("first") == "Test123"
        assert resolver.resolve("second") == "Test456"

    def test_should_not_resolve_non_string_data(self, holder_mock):

        from savegem.app.gui.widget.resolver.holder import DataResolver

        holder_mock.get.side_effect = lambda key: {
            "function": lambda: None,
            "integer": 123,
            "object": {}
        }.get(key)

        resolver = DataResolver()
        assert resolver.resolve("function") == ""
        assert resolver.resolve("integer") == ""
        assert resolver.resolve("object") == ""
