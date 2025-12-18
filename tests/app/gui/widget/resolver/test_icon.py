import pytest


TEST_PATH = "/test/path/to/file.jpg"
TEST_RESOLVED_PATH = "resolved/test/path/to/file.jpg"


class TestIconResolver:

    @pytest.fixture(autouse=True)
    def _setup(self, resolve_resource_mock):
        resolve_resource_mock.return_value = TEST_RESOLVED_PATH

    @pytest.fixture
    def _icon_mock(self, module_patch):
        return module_patch("QIcon")

    def test_invalid_file_path(self, _icon_mock):

        from savegem.app.gui.widget.resolver.icon import IconResolver

        resolver = IconResolver()
        resolved_value = resolver.resolve(None)  # noqa

        assert resolved_value is None

    def test_no_size(self, _icon_mock):

        from savegem.app.gui.widget.resolver.icon import IconResolver

        resolver = IconResolver()
        resolved_value = resolver.resolve(TEST_PATH)

        _icon_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        assert resolved_value.width == IconResolver.DefaultSize
        assert resolved_value.height == IconResolver.DefaultSize

    def test_one_dimension_defined(self, _icon_mock):

        from savegem.app.gui.widget.resolver.icon import IconResolver

        resolver = IconResolver()
        resolved_value = resolver.resolve(TEST_PATH, width=100)

        assert resolved_value.width == 100
        assert resolved_value.height == IconResolver.DefaultSize

        resolved_value = resolver.resolve(TEST_PATH, height=100)

        assert resolved_value.width == IconResolver.DefaultSize
        assert resolved_value.height == 100

        resolved_value = resolver.resolve(TEST_PATH, width=200, height=100)

        assert resolved_value.width == 200
        assert resolved_value.height == 100

    def test_size_and_dimension_defined(self, _icon_mock):

        from savegem.app.gui.widget.resolver.icon import IconResolver

        resolver = IconResolver()
        resolved_value = resolver.resolve(TEST_PATH, size=100, width=200)

        assert resolved_value.width == 200
        assert resolved_value.height == 100
