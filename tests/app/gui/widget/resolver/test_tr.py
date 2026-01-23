

class TestTrResolver:

    def test_no_args(self, tr_mock):

        from src.savegem import TrResolver

        resolver = TrResolver()
        resolver.resolve("name", "John")
        resolver.resolve("another")

        tr_mock.assert_any_call("name", "John")
        tr_mock.assert_any_call("another")
