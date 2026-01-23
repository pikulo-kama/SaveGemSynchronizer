import re
from unittest.mock import call

import pytest
from PyQt6.QtCore import Qt
from pytest_mock import MockerFixture


class TestStyle:

    @pytest.fixture(autouse=True)
    def _setup(self, path_join_mock, resolve_resource_mock, db_mock, app_state_mock):

        from src.savegem import DatabaseRow
        from src.savegem import ColorMode

        color_table_columns = ["color_id", ColorMode.Light, ColorMode.Dark]
        font_table_columns = ["font_id", "font_size", "font_family", "font_weight"]
        resource_table_columns = ["resource_name", "resource_path", "color"]

        colors = [
            DatabaseRow(1, ("background", "#FFFFFF", "#1E1E1E"), color_table_columns),
            DatabaseRow(2, ("text", "#000000", "#EBEBEB"), color_table_columns),
        ]

        fonts = [
            DatabaseRow(1, ("main_text", 14, "Arial", None), font_table_columns),
            DatabaseRow(2, ("title_text", 24, "Roboto Bold", 800), font_table_columns),
        ]

        resources = [
            DatabaseRow(1, ("checkmark", "checkmark", "background"), resource_table_columns),
            DatabaseRow(2, ("checkmark_alt", "checkmark", "text"), resource_table_columns),
            DatabaseRow(2, ("checkmark_bad", "checkmark", None), resource_table_columns),
        ]

        db_mock.retrieve_table.side_effect = lambda table_name: {
            "setup_color": colors,
            "setup_font": fonts,
            "setup_resource": resources
        }.get(table_name)

        resolve_resource_mock.side_effect = lambda path: f"resolved/path/{path}"
        app_state_mock.color_theme = None


    @pytest.fixture
    def _mock_color_scheme(self, qt_app_mock):
        def _mock_scheme(color_scheme):
            qt_app_mock.instance.return_value \
                .styleHints.return_value \
                .colorScheme.return_value = color_scheme

        return _mock_scheme


    def test_get_color_mode_light(self, _mock_color_scheme):
        """
        Test that _get_color_mode returns 'light' for Qt.ColorScheme.Light.
        """

        from src.savegem import ColorMode, get_system_color_mode

        _mock_color_scheme(Qt.ColorScheme.Light)
        assert get_system_color_mode() == ColorMode.Light


    def test_get_color_mode_dark(self, _mock_color_scheme):
        """
        Test that _get_color_mode returns 'dark' for Qt.ColorScheme.Dark.
        """

        from src.savegem import ColorMode, get_system_color_mode

        _mock_color_scheme(Qt.ColorScheme.Dark)
        assert get_system_color_mode() == ColorMode.Dark


    def test_get_color_mode_default_light(self, _mock_color_scheme, qt_app_mock):
        """
        Test that _get_color_mode returns 'light' for an unrecognized scheme (default).
        """

        from src.savegem import ColorMode, get_system_color_mode

        # Use an arbitrary int not matching Light (1) or Dark (2)
        _mock_color_scheme(99)
        assert get_system_color_mode() == ColorMode.Light

        _mock_color_scheme(ColorMode.Dark)
        qt_app_mock.instance.return_value = None

        assert get_system_color_mode() == ColorMode.Light


    def test_color_light_mode(self, _mock_color_scheme, app_state_mock):
        """
        Test _color retrieves the correct color in light mode.
        """

        from src.savegem import color

        _mock_color_scheme(Qt.ColorScheme.Light)

        assert color("background") == "#FFFFFF"
        assert color("text") == "#000000"


    def test_color_dark_mode(self, _mock_color_scheme, app_state_mock):
        """
        Test _color retrieves the correct color in dark mode.
        """

        from src.savegem import color

        _mock_color_scheme(Qt.ColorScheme.Dark)

        assert color("background") == "#1E1E1E"
        assert color("text") == "#EBEBEB"


    def test_color_from_settings(self, _mock_color_scheme, app_state_mock):

        from src.savegem import color, ColorMode

        app_state_mock.color_theme = ColorMode.Light
        _mock_color_scheme(Qt.ColorScheme.Dark)

        # Even if system color mode is Dark, configuration
        # in user settings (app state) should have higher precedence.
        assert color("background") == "#FFFFFF"
        assert color("text") == "#000000"


    def test_font(self):
        """
        Test _font retrieves the correct font property.
        """

        from src.savegem import font

        assert font("main_text") == "14px 'Arial'; font-weight: 400"
        assert font("title_text") == "24px 'Roboto Bold'; font-weight: 800"


    def test_rgba_color(self, module_patch):

        from src.savegem import rgba_color

        module_patch("color").return_value = "#1E1E1E"

        assert rgba_color("test", "0.5123") == "rgba(30, 30, 30, 0.5123)"


    def test_resolve_style_properties(self, _mock_color_scheme):
        """
        Test _resolve_style_properties correctly replaces color(), font(), and image() tokens.
        """

        from src.savegem import resolve_style_properties

        _mock_color_scheme(Qt.ColorScheme.Dark)

        input_style = """
            background-color: color('background');
            font-family: font('main_text');
            border-image: image('button.png');
            padding: 5px;
        """

        expected_style = """
            background-color: #1E1E1E;
            font-family: 14px 'Arial'; font-weight: 400;
            border-image: url('resolved/path/button.png');
            padding: 5px;
        """

        result = resolve_style_properties(input_style)

        # Remove whitespace for a reliable comparison
        clean_result = re.sub(r'\s+', '', result)
        clean_expected = re.sub(r'\s+', '', expected_style)

        assert clean_result == clean_expected


    def test_load_stylesheet(self, listdir_mock, read_file_mock, _mock_color_scheme):
        """
        Test load_stylesheet reads all files, concatenates them, and resolves properties.
        """

        from src.savegem.constants import Directory
        from src.savegem import load_stylesheet

        _mock_color_scheme(Qt.ColorScheme.Light)

        # Mock os.listdir to simulate 3 style files
        listdir_mock.return_value = ["base.qss", "buttons.qss", "specific.qss"]

        # Mock read_file to return different resolver for each file
        def mock_read_file_side_effect(path):
            if "base.qss" in path:
                return "QWidget { color: color('text'); }"

            elif "buttons.qss" in path:
                return "QPushButton { font: font('title_text'); }"

            elif "specific.qss" in path:
                return "QLabel { background: image('label.png'); }"

            return ""

        read_file_mock.side_effect = mock_read_file_side_effect

        # Expected resolved string in Light Mode
        expected_resolved_string = (
            "QWidget { color: #000000; }"  # Light mode color
            "QPushButton { font: 24px 'Roboto Bold'; font-weight: 800; }"  # Font
            "QLabel { background: url('resolved/path/label.png'); }"  # Image token
        )

        result = load_stylesheet()

        # Assert that os.listdir and os.path.join were called correctly (mocked in fixture)
        listdir_mock.assert_called_with(Directory().Styles)
        assert read_file_mock.call_count == 3

        # Check the final resolved string
        clean_result = re.sub(r'\s+', '', result)
        clean_expected = re.sub(r'\s+', '', expected_resolved_string)

        assert clean_result == clean_expected


    def test_load_stylesheet_with_sub_dir(self, mocker: MockerFixture, module_patch, listdir_mock, read_file_mock,
                                          _mock_color_scheme, path_mock):

        from src.savegem import load_stylesheet

        resolve_props_mock = module_patch("resolve_style_properties")
        resolve_props_mock.side_effect = lambda style: style

        dir_path_mock = mocker.Mock()
        file_path_mock = mocker.Mock()

        dir_path_mock.is_dir.return_value = True
        file_path_mock.is_dir.return_value = False

        listdir_mock.side_effect = [["file1", "file2", "subdir"], ["file3"]]
        read_file_mock.side_effect = lambda path: f"{path} "
        path_mock.side_effect = [file_path_mock, file_path_mock, dir_path_mock, file_path_mock]

        load_stylesheet("")

        assert resolve_props_mock.call_count == 2
        resolve_props_mock.assert_has_calls([
            call("/subdir/file3 "),  # first subdirectory
            call("/file1 /file2 /subdir/file3 "),  # then both subdirectory with files from main dir
        ])


    def test_dynamic_resource_creation(self, save_file_mock, read_file_mock, resolve_resource_mock,
                                       resolve_temp_resource_mock, logger_mock, _mock_color_scheme):
        """
        Tests that dynamic images are fetched from DB,
        colors are resolved, content is replaced, and files are saved.
        """

        from src.savegem import create_dynamic_resources, ColorMode

        read_file_mock.return_value = '<svg fill="currentColor" />'
        _mock_color_scheme(ColorMode.Dark)

        # Setup Path Resolution (Just pass through strings for verification)
        resolve_resource_mock.side_effect = lambda path, include_temporary: f"/resolved/{path}"
        resolve_temp_resource_mock.side_effect = lambda name: f"/temp/{name}.svg"

        create_dynamic_resources()

        resolve_resource_mock.assert_has_calls([
            call("checkmark", include_temporary=False),
            call("checkmark", include_temporary=False)
        ])

        save_file_mock.assert_has_calls([
            call("/temp/checkmark.svg", "<svg fill=\"#FFFFFF\" />"),
            call("/temp/checkmark_alt.svg", "<svg fill=\"#000000\" />"),
            call("/temp/checkmark_bad.svg", "<svg fill=\"\" />")
        ], any_order=True)

        assert save_file_mock.call_count == 3
