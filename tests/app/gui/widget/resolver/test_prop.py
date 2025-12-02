

class TestPropResolver:

    def test_resolve(self, prop_mock):

        from savegem.app.gui.widget.resolver.prop import PropResolver

        prop_mock.side_effect = lambda key: {
            "prop1": "first",
            "prop2": "second"
        }.get(key)

        resolver = PropResolver()
        assert resolver.resolve("prop1") == "first"
        assert resolver.resolve("prop2") == "second"
