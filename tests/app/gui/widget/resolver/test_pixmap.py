import pytest


TEST_PATH = "/test/path/to/file.jpg"
TEST_RESOLVED_PATH = "resolved/test/path/to/file.jpg"

class TestPixmapResolver:

    @pytest.fixture(autouse=True)
    def _setup(self, resolve_resource_mock, _scale_image_mock, _round_image_mock, _pixmap_mock):
        resolve_resource_mock.return_value = TEST_RESOLVED_PATH

        _scale_image_mock.return_value = _pixmap_mock.return_value
        _round_image_mock.return_value = _pixmap_mock.return_value

    @pytest.fixture
    def _pixmap_mock(self, module_patch):
        return module_patch("QPixmap")

    @pytest.fixture
    def _scale_image_mock(self, module_patch):
        return module_patch("scale_image")

    @pytest.fixture
    def _round_image_mock(self, module_patch):
        return module_patch("round_image")

    def test_file_path_is_none(self, _pixmap_mock, logger_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(None)  # noqa

        # If file path is not provided will create empty pixmap
        # that's why we don't expect any arguments.
        _pixmap_mock.assert_called_once()
        logger_mock.error.assert_called_once()

    def test_no_props(self, _scale_image_mock, _round_image_mock, _pixmap_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH)

        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_not_called()
        _scale_image_mock.assert_not_called()

    def test_with_scale(self, _scale_image_mock, _round_image_mock, _pixmap_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH, scale=20)

        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_not_called()
        _scale_image_mock.assert_called_once_with(_pixmap_mock.return_value, 20)

    def test_with_radius(self, _scale_image_mock, _round_image_mock, _pixmap_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH, radius=20)

        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_called_once_with(_pixmap_mock.return_value, 20)
        _scale_image_mock.assert_not_called()

    def test_with_circle(self, _scale_image_mock, _round_image_mock, _pixmap_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH, "circle")

        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_called_once_with(_pixmap_mock.return_value)
        _scale_image_mock.assert_not_called()

    def test_with_radius_and_circle(self, _scale_image_mock, _round_image_mock, _pixmap_mock):

        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH, "circle", radius=20)

        # Circle has higher priority than radius.
        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_called_once_with(_pixmap_mock.return_value)
        _scale_image_mock.assert_not_called()

    def test_scale_and_radius(self, _scale_image_mock, _round_image_mock, _pixmap_mock):
        from savegem.app.gui.widget.resolver.pixmap import PixmapResolver

        resolver = PixmapResolver()
        resolver.resolve(TEST_PATH, scale=30, radius=20)

        # Circle has higher priority than radius.
        _pixmap_mock.assert_called_once_with(TEST_RESOLVED_PATH)
        _round_image_mock.assert_called_once_with(_pixmap_mock.return_value, 20)
        _scale_image_mock.assert_called_once_with(_pixmap_mock.return_value, 30)
