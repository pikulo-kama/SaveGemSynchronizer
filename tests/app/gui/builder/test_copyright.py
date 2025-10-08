from datetime import date
from unittest.mock import call

import pytest
from PyQt6.QtCore import Qt
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(prop_mock, tr_mock):
    prop_mock.side_effect = lambda key: {
        "name": "SaveGem",
        "version": "1.2.0",
        "author": "Author A",
    }.get(key)

    def _tr(key, *args):

        if key == "window_Copyright":
            return f"Copyright String: {args[0]} v{args[1]}, {args[2]} by {args[3]}"
        else:
            return f"Disclaimer for {args[0]}"

    tr_mock.side_effect = _tr


@pytest.fixture
def _copyright_builder(gui_mock):
    """
    Provides a fully mocked and initialized CopyrightBuilder instance.
    """

    from savegem.app.gui.builder.copyright import CopyrightBuilder

    builder = CopyrightBuilder()
    builder._gui = gui_mock

    return builder


def test_copyright_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor correctly initializes the base class.
    """

    from savegem.app.gui.builder import UIBuilder
    from savegem.app.gui.builder.copyright import CopyrightBuilder
    from savegem.app.gui.constants import UIRefreshEvent

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)

    builder = CopyrightBuilder()

    mock_super_init.assert_called_once_with(UIRefreshEvent.LanguageChange)
    assert builder._CopyrightBuilder__copyright is None  # noqa


def test_build_creates_label_and_adds_to_gui(module_patch, gui_mock, _copyright_builder):
    """
    Test build() creates the QLabel, sets its name, and adds it to the correct layout.
    """

    frame_mock = module_patch("QWidget")
    frame_layout = module_patch("QHBoxLayout")

    mock_label_constructor = module_patch("QLabel")
    mock_label_instance = mock_label_constructor.return_value

    mock_tooltip_constructor = module_patch("QIconTooltip")
    mock_tooltip_instance = mock_tooltip_constructor.return_value

    _copyright_builder.build()

    mock_label_constructor.assert_called_once_with()
    mock_tooltip_constructor.assert_called_once_with()
    mock_label_instance.setObjectName.assert_called_once_with("copyright")

    frame_layout.return_value.addWidget.assert_has_calls([
        call(mock_label_instance, alignment=Qt.AlignmentFlag.AlignVCenter),
        call(mock_tooltip_instance, alignment=Qt.AlignmentFlag.AlignVCenter)
    ])

    gui_mock.bottom.layout.return_value.addWidget.assert_called_once_with(frame_mock.return_value, 0)


@pytest.mark.parametrize("mock_year, expected_period", [
    (2023, "2023"),
    (2024, "2023-2024"),
    (2030, "2023-2030"),
])
def test_refresh_calculates_period_and_sets_text(mocker: MockerFixture, _copyright_builder, date_mock, mock_year,
                                                 expected_period, tr_mock):
    """
    Test refresh() correctly calculates the copyright year period and calls 'tr'.
    """

    # Arrange: Mock the current date
    date_mock.today.return_value = date(mock_year, 1, 1)

    mock_copyright_label = mocker.MagicMock()
    mock_disclaimer_label = mocker.MagicMock()

    _copyright_builder._CopyrightBuilder__copyright = mock_copyright_label
    _copyright_builder._CopyrightBuilder__tooltip = mock_disclaimer_label

    _copyright_builder.refresh()

    # Assert 1: tr() is called with the correct arguments
    tr_mock.assert_has_calls([
        call(
            "window_CopyrightDisclaimer",
            "SaveGem"
        ),
        call(
            "window_Copyright",
            "SaveGem",
            "1.2.0",
            expected_period,
            "Author A"
        )
    ])

    expected_copyright = f"Copyright String: SaveGem v1.2.0, {expected_period} by Author A"
    expected_disclaimer = f"Disclaimer for SaveGem"

    mock_copyright_label.setText.assert_called_once_with(expected_copyright)
    mock_disclaimer_label.setText.assert_called_once_with(expected_disclaimer)


def test_refresh_logs_info(mocker: MockerFixture, _copyright_builder, logger_mock):
    """
    Test refresh() ensures the logger debug method is called.
    """

    _copyright_builder._CopyrightBuilder__copyright = mocker.MagicMock()
    _copyright_builder._CopyrightBuilder__tooltip = mocker.MagicMock()

    _copyright_builder.refresh()

    logger_mock.debug.call_count = 2
    assert "Disclaimer was reloaded" in logger_mock.debug.call_args_list[0][0][0]
    assert "Copyright was reloaded" in logger_mock.debug.call_args_list[1][0][0]
