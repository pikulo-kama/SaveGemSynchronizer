import sys
import pytest


class MockBaseClass:
    """
    The base class we are looking for (the 'clazz' argument).
    """
    pass


class SubClassA(MockBaseClass):
    """
    A valid subclass found in module_a.
    """
    pass


class SubClassB(MockBaseClass):
    """
    A valid subclass found in module_b.
    """
    pass


class NonSubClass:
    """
    An irrelevant class.
    """
    pass


class TestReflectionUtil:

    @pytest.fixture
    def _package_mock(self, mocker, module_patch):
        """
        Sets up the necessary mocks for sys, pkgutil, importlib, and inspect
        to simulate iterating over a package containing two modules.

        This replaces the need for an actual package structure on disk.
        """

        mock_package_name = "mock_package"

        mock_module_a_members = [
            (SubClassA.__name__, SubClassA),
            (NonSubClass.__name__, NonSubClass)
        ]

        mock_module_b_members = [
            (SubClassB.__name__, SubClassB),
            (MockBaseClass.__name__, MockBaseClass)
        ]

        mock_module_a = mocker.MagicMock()
        mock_module_b = mocker.MagicMock()

        mock_package = mocker.MagicMock()
        mock_package.__path__ = ["/mock/path"]
        sys.modules[mock_package_name] = mock_package

        mock_inspect = module_patch("inspect")
        pkgutil_mock = module_patch("pkgutil")
        mock_import_lib = module_patch("importlib")

        pkgutil_mock.iter_modules.return_value = [
            (mocker.MagicMock(), "module_a", False),
            (mocker.MagicMock(), "module_b", False),
        ]

        mock_import_lib.import_module.side_effect = [mock_module_a, mock_module_b]
        mock_inspect.getmembers.side_effect = [mock_module_a_members, mock_module_b_members]

        yield mock_package_name


    def test_get_members_finds_all_subclasses(self, _package_mock):
        """
        Tests that get_members successfully iterates over mocked modules and
        yields all classes that are subclasses of the target class, but not the target class itself.
        """

        from savegem.common.util.reflection import get_members

        # Assumes "mock_package" is configured by the external setup
        target_clazz = MockBaseClass

        # The expected results (class name, class object)
        expected_members = {
            ("SubClassA", SubClassA),
            ("SubClassB", SubClassB)
        }

        # Run the generator function and collect results
        found_members = set(get_members(_package_mock, target_clazz))

        # Assert that exactly the two expected subclasses were found
        assert found_members == expected_members

        # Assert that the number of returned members is correct
        assert len(found_members) == 2


    def test_get_members_excludes_base_class(self, _package_mock):
        """
        Tests the condition 'member is not clazz', ensuring the base class itself
        is never yielded, even if inspect.getmembers finds it.
        """

        from savegem.common.util.reflection import get_members

        target_clazz = MockBaseClass

        # Run the generator function
        found_members = list(get_members(_package_mock, target_clazz))

        # Assert that the MockBaseClass is not in the results
        for _, member_class in found_members:
            assert member_class is not target_clazz


    def test_get_members_excludes_non_subclasses(self, _package_mock):
        """
        Tests the condition 'issubclass(member, clazz)', ensuring classes that
        do not inherit from the target class are excluded.
        """

        from savegem.common.util.reflection import get_members

        target_clazz = MockBaseClass

        # Run the generator function
        found_members = list(get_members(_package_mock, target_clazz))

        # Assert that the NonSubClass is not in the results
        for _, member_class in found_members:
            assert member_class is not NonSubClass
