import pytest
from pytest_mock import MockerFixture


class ResolverTestModuleHelper:

    @pytest.fixture(autouse=True)
    def _setup(self, module_patch, get_members_mock, _mock_resolvers):

        def get_resolvers_mock(_, __):
            for resolver_class in _mock_resolvers.values():
                yield resolver_class.__name__, resolver_class

        get_members_mock.side_effect = get_resolvers_mock

    @pytest.fixture
    def _mock_token_resolver(self):
        from savegem.app.gui.widget.resolver import ContentResolver

        # Define concrete resolver implementations for testing
        class MockTokenResolver(ContentResolver):
            def resolve(self, value: str, *args, **kw):
                # Returns a string to test substitution
                return f"TOKEN_RES:{value}, {kw.get('scaled')}"

        return MockTokenResolver

    @pytest.fixture
    def _mock_integer_resolver(self):
        from savegem.app.gui.widget.resolver import ContentResolver

        class MockIntegerResolver(ContentResolver):
            def resolve(self, value: str, *args, **kw):
                # Returns an integer to test exit condition
                return 12345

        return MockIntegerResolver

    @pytest.fixture
    def _mock_no_sub_resolver(self):
        from savegem.app.gui.widget.resolver import ContentResolver

        class MockNoSubsResolver(ContentResolver):
            def resolve(self, value: str, *args, **kw):
                # Returns the parameter directly to test recursion stop
                return value

        return MockNoSubsResolver

    @pytest.fixture
    def _mock_resolvers(self, _mock_token_resolver, _mock_integer_resolver, _mock_no_sub_resolver):
        return {
            "mocktokenresolver": _mock_token_resolver,
            "mockintegerresolver": _mock_integer_resolver,
            "mocknosubsresolver": _mock_no_sub_resolver,
        }


class TestContentResolverFactory(ResolverTestModuleHelper):

    def test_get_resolver_lazy_loading(self, get_members_mock, _mock_token_resolver):
        """
        Test that resolvers are loaded only once (lazy loading/singleton).
        """

        from savegem.app.gui.widget.resolver import get_resolver

        # 1. First call loads the pool
        resolver_1 = get_resolver("mocktokenresolver")

        # 2. Second call should hit the cache
        resolver_2 = get_resolver("MOCKTOKENRESOLVER")

        # Assert get_members was called only once
        get_members_mock.assert_called()

        # Assert the same instance is returned (singleton pattern)
        assert resolver_1 is resolver_2
        assert isinstance(resolver_1, _mock_token_resolver)


class TestResolveContent(ResolverTestModuleHelper):

    @pytest.fixture
    def _mock_token_resolve_method(self, mocker: MockerFixture):
        from savegem.app.gui.widget.resolver import get_resolver
        return mocker.patch.object(get_resolver("mocktokenresolver"), "resolve")

    def test_no_token_returns_string(self):
        """
        Test simple string without tokens is returned unchanged.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        content = "This is plain text."
        assert resolve_content(content) == content

    def test_simple_token_resolution(self):
        """
        Test resolution of a simple, single token.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        content = "mocktoken{value, scaled: 100}"
        resolved = resolve_content(content)

        assert resolved == "TOKEN_RES:value, 100"

    def test_token_with_digital_properties(self, _mock_token_resolve_method):
        """
        Test that properties that look like digits are converted to int.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        content = "mocktoken{param, key1: 42, key2: 99}"
        resolve_content(content)

        _mock_token_resolve_method.assert_called_once_with("param", key1=42, key2=99)

    def test_token_with_positional_arguments(self, _mock_token_resolve_method):
        """
        Test a token that only has positional arguments after the main parameter.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        content = "mocktoken{param, arg1, arg2: val}"
        resolve_content(content)

        _mock_token_resolve_method.assert_called_once_with("param", "arg1", arg2="val")

    def test_nested_token_recursion(self, mocker: MockerFixture):
        """
        Test the complex case: nested tokens are resolved before the outer token,
        and the resulting non-string object breaks the outer loop correctly.
        """

        from savegem.app.gui.widget.resolver import resolve_content, get_resolver

        token_resolve = mocker.spy(get_resolver("mocktokenresolver"), "resolve")
        integer_resolve = mocker.spy(get_resolver("mockintegerresolver"), "resolve")

        #    Outer Token: mocktoken{...}
        #    Inner Token (Parameter): mockinteger{100}
        resolved_value = resolve_content("mocktoken{mockinteger{100}, scaled: 10}")

        integer_resolve.assert_called_once_with("100")
        token_resolve.assert_called_once_with(12345, scaled=10)

        assert resolved_value == "TOKEN_RES:12345, 10"

    def test_token_next_to_text(self):
        """
        Test substitution when token is combined with literal text.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        resolved = resolve_content("The logo is: mocktoken{user_id, scaled: 10}.")
        assert resolved == "The logo is: TOKEN_RES:user_id, 10."

    def test_token_returning_none(self, _mock_token_resolve_method):
        """
        Test token resolution resulting in None should resolve to empty string.
        """

        from savegem.app.gui.widget.resolver import resolve_content

        _mock_token_resolve_method.return_value = None
        resolved = resolve_content("Result: mocktoken{none_value}.")

        assert resolved == "Result: ."
