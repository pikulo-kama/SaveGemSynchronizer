from datetime import date

import pytest
from PyQt6.QtWidgets import QVBoxLayout, QLabel
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _setup(prop_mock, tr_mock):
    prop_mock.side_effect = lambda key: {
        "name": "SaveGem",
        "version": "1.2.0",
        "author": "Author A",
    }.get(key)

    tr_mock.side_effect = lambda key, name, version, period, author: \
        f"Copyright String: {name} v{version}, {period} by {author}"


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


def test_build_creates_label_and_adds_to_gui(mocker: MockerFixture, module_patch, gui_mock, _copyright_builder):
    """
    Test build() creates the QLabel, sets its name, and adds it to the correct layout.
    """

    mock_label_constructor = module_patch("QLabel")
    mock_label_instance = mock_label_constructor.return_value

    mock_layout = mocker.MagicMock(spec=QVBoxLayout)
    gui_mock.bottom.layout.return_value = mock_layout

    _copyright_builder.build()

    mock_label_constructor.assert_called_once_with()
    mock_label_instance.setObjectName.assert_called_once_with("copyright")
    mock_layout.addWidget.assert_called_once_with(mock_label_instance, 0)

    assert _copyright_builder._CopyrightBuilder__copyright is mock_label_instance  # noqa


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

    mock_label = mocker.MagicMock(spec=QLabel)
    _copyright_builder._CopyrightBuilder__copyright = mock_label

    _copyright_builder.refresh()

    # Assert 1: tr() is called with the correct arguments
    tr_mock.assert_called_once_with(
        "window_Copyright",
        "SaveGem",
        "1.2.0",
        expected_period,
        "Author A"
    )

    expected_text = f"Copyright String: SaveGem v1.2.0, {expected_period} by Author A"
    mock_label.setText.assert_called_once_with(expected_text)


def test_refresh_logs_info(mocker: MockerFixture, _copyright_builder, logger_mock):
    """
    Test refresh() ensures the logger debug method is called.
    """

    mock_label = mocker.MagicMock(spec=QLabel)
    _copyright_builder._CopyrightBuilder__copyright = mock_label

    _copyright_builder.refresh()

    logger_mock.debug.assert_called_once()
    assert "Copyright was reloaded" in logger_mock.debug.call_args[0][0]
