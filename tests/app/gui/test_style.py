import re

import pytest
from PyQt6.QtCore import Qt

from constants import Directory
from savegem.app.gui.style import load_stylesheet, _COLOR_MODE_LIGHT, _COLOR_MODE_DARK  # noqa
from savegem.app.gui.style import _resolve_style_properties  # noqa
from savegem.app.gui.style import _get_color_mode  # noqa
from savegem.app.gui.style import _color  # noqa
from savegem.app.gui.style import _font  # noqa
from savegem.app.gui.style import _image  # noqa
from tests.tools.mocks.mock_json_config_holder import MockJsonConfigHolder


@pytest.fixture(autouse=True)
def _setup(json_config_holder_mock, path_join_mock, resolve_resource_mock):
    json_config_holder_mock.return_value = MockJsonConfigHolder(
        {
            "colors": {
                "light": {
                    "background": "#FFFFFF",
                    "text": "#000000",
                },
                "dark": {
                    "background": "#1E1E1E",
                    "text": "#EBEBEB",
                }
            },
            "fonts": {
                "main_text": "Arial",
                "title_text": "Roboto Bold",
            }
        }
    )

    resolve_resource_mock.side_effect = lambda path: f"resolved/path/{path}"


@pytest.fixture
def _mock_color_scheme(qt_app_mock):
    def _mock_scheme(color_scheme):
        qt_app_mock.instance.return_value \
            .styleHints.return_value \
            .colorScheme.return_value = color_scheme

    return _mock_scheme


def test_get_color_mode_light(_mock_color_scheme):
    """
    Test that _get_color_mode returns 'light' for Qt.ColorScheme.Light.
    """

    _mock_color_scheme(Qt.ColorScheme.Light)
    assert _get_color_mode() == _COLOR_MODE_LIGHT


def test_get_color_mode_dark(_mock_color_scheme):
    """
    Test that _get_color_mode returns 'dark' for Qt.ColorScheme.Dark.
    """

    _mock_color_scheme(Qt.ColorScheme.Dark)
    assert _get_color_mode() == _COLOR_MODE_DARK


def test_get_color_mode_default_light(_mock_color_scheme):
    """
    Test that _get_color_mode returns 'light' for an unrecognized scheme (default).
    """

    # Use an arbitrary int not matching Light (1) or Dark (2)
    _mock_color_scheme(99)
    assert _get_color_mode()


def test_color_light_mode(_mock_color_scheme):
    """
    Test _color retrieves the correct color in light mode.
    """

    _mock_color_scheme(Qt.ColorScheme.Light)

    assert _color("background") == "#FFFFFF"
    assert _color("text") == "#000000"


def test_color_dark_mode(_mock_color_scheme):
    """
    Test _color retrieves the correct color in dark mode.
    """

    _mock_color_scheme(Qt.ColorScheme.Dark)

    assert _color("background") == "#1E1E1E"
    assert _color("text") == "#EBEBEB"


def test_font():
    """
    Test _font retrieves the correct font property.
    """

    assert _font("main_text") == "Arial"
    assert _font("title_text") == "Roboto Bold"


def test_image(_mock_color_scheme, resolve_resource_mock):
    """
    Test _image resolves the resource path correctly, uses the color mode,
    and replaces OS separators with forward slashes for QSS format.
    """

    # Set to dark mode
    _mock_color_scheme(Qt.ColorScheme.Dark)

    # Expected path: dark/icon.png
    expected_resolved_path = "resolved/path/dark/icon.png"
    expected_token = f"url('{expected_resolved_path}')"

    result = _image("icon.png")

    # Check the call to resolve_resource used the correct OS path format (dark\icon.png)
    # The lambda in the fixture handles the os.path.join mocking here
    assert "dark/icon.png" in resolve_resource_mock.call_args[0][0]
    assert result == expected_token


def test_resolve_style_properties(_mock_color_scheme):
    """
    Test _resolve_style_properties correctly replaces color(), font(), and image() tokens.
    """

    _mock_color_scheme(Qt.ColorScheme.Dark)

    input_style = """
        background-color: color("background");
        font-family: font('main_text');
        border-image: image('button.png');
        padding: 5px;
    """

    expected_style = """
        background-color: #1E1E1E;
        font-family: Arial;
        border-image: url('resolved/path/dark/button.png');
        padding: 5px;
    """

    result = _resolve_style_properties(input_style)

    # Remove whitespace for a reliable comparison
    clean_result = re.sub(r'\s+', '', result)
    clean_expected = re.sub(r'\s+', '', expected_style)

    assert clean_result == clean_expected


def test_load_stylesheet(listdir_mock, read_file_mock, _mock_color_scheme):
    """
    Test load_stylesheet reads all files, concatenates them, and resolves properties.
    """
    _mock_color_scheme(Qt.ColorScheme.Light)

    # Mock os.listdir to simulate 3 style files
    listdir_mock.return_value = ["base.qss", "buttons.qss", "specific.qss"]

    # Mock read_file to return different content for each file
    def mock_read_file_side_effect(path):
        if "base.qss" in path:
            return "QWidget { color: color('text'); }"

        elif "buttons.qss" in path:
            return "QPushButton { font: font('title_text'); }"

        elif "specific.qss" in path:
            return "QLabel { background: image('label.png'); }"

    read_file_mock.side_effect = mock_read_file_side_effect

    # Expected resolved string in Light Mode
    expected_resolved_string = (
        "QWidget { color: #000000; }"  # Light mode color
        "QPushButton { font: Roboto Bold; }"  # Font
        "QLabel { background: url('resolved/path/light/label.png'); }"  # Image token
    )

    result = load_stylesheet()

    # Assert that os.listdir and os.path.join were called correctly (mocked in fixture)
    listdir_mock.assert_called_with(Directory.Styles)
    assert read_file_mock.call_count == 3

    # Check the final resolved string
    clean_result = re.sub(r'\s+', '', result)
    clean_expected = re.sub(r'\s+', '', expected_resolved_string)

    assert clean_result == clean_expected
