import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton
from pytest_mock import MockerFixture

from savegem.app.gui.builder import UIBuilder
from savegem.app.gui.builder.language_switch import LanguageSwitchBuilder
from savegem.app.gui.constants import UIRefreshEvent, QAttr, QKind, QObjectName


@pytest.fixture(autouse=True)
def _setup_dependencies(tr_mock, locales_mock, app_context, app_state_mock):
    tr_mock.side_effect = lambda key: "en_US" if key == "languageId" else f"Translated({key})"
    locales_mock.return_value = ["en_US", "fr_FR", "de_DE"]
    app_state_mock.locale = "en_US"


@pytest.fixture
def _language_switch_builder(simple_gui):
    """
    Provides a fully mocked and initialized LanguageSwitchBuilder instance.
    """

    builder = LanguageSwitchBuilder()
    builder._gui = simple_gui

    return builder


def test_builder_initialization(mocker: MockerFixture):
    """
    Test the constructor initializes the base class with the correct event.
    """

    mock_super_init = mocker.patch.object(UIBuilder, '__init__', return_value=None)
    builder = LanguageSwitchBuilder()

    mock_super_init.assert_called_once_with(UIRefreshEvent.LanguageChange)
    assert builder._LanguageSwitchBuilder__language_switch is None  # noqa


@pytest.mark.parametrize("locale_count, expected_enabled", [
    (1, False),  # Disabled if only one locale
    (2, True),  # Enabled if two or more
    (3, True),
])
def test_is_enabled_based_on_locale_count(locales_mock, locale_count, expected_enabled):
    """
    Test is_enabled() returns True only if there are multiple locales configured.
    """

    # Arrange
    locales_mock.return_value = ["L"] * locale_count
    builder = LanguageSwitchBuilder()

    # Act / Assert
    assert builder.is_enabled() == expected_enabled


def test_build_creates_button_and_registers_it(mocker: MockerFixture, _language_switch_builder, simple_gui):
    """
    Test build() creates the button, connects the callback, and adds it to the layout.
    """

    # Arrange: Spy on internal methods
    mock_add_interactable = mocker.patch.object(_language_switch_builder, '_add_interactable')

    # Act
    _language_switch_builder.build()

    button = _language_switch_builder._LanguageSwitchBuilder__language_switch  # noqa

    # Assert 1: Button creation and properties
    assert isinstance(button, QPushButton)
    assert button.objectName() == QObjectName.SquareButton
    assert button.property(QAttr.Kind) == QKind.Primary

    # Assert 2: Button is registered as interactable
    mock_add_interactable.assert_called_once_with(button)

    # Assert 3: Button is added to the GUI layout with correct placement
    simple_gui.top_left.layout().addWidget.assert_called_once_with(
        button, 1, 0,
        alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
    )


@pytest.mark.parametrize("tr_return, expected_text", [
    ("en_US", "en"),  # Standard trim
    ("fr", "fr"),  # No trim needed
    ("zh_CN_extended", "zh")  # Extended trim
])
def test_refresh_sets_button_text_and_trims(_language_switch_builder, tr_mock, logger_mock, tr_return, expected_text):
    """
    Test 'refresh' calls 'tr' for languageId and trims the result to 2 characters.
    """

    # Arrange: Setup button and mocks
    _language_switch_builder.build()
    mock_button = _language_switch_builder._LanguageSwitchBuilder__language_switch  # noqa
    # Reset side effect.
    tr_mock.side_effect = None
    tr_mock.return_value = tr_return

    # Act
    _language_switch_builder.refresh()

    # Assert 1: tr() is called
    tr_mock.assert_called_once_with("languageId")

    # Assert 2: Button text is set and trimmed
    assert mock_button.text() == expected_text

    # Assert 3: Logging is performed
    logger_mock.debug.call_count = 2  # once for build and once for refresh.
    logger_mock.debug.assert_called_with(
        "Refreshing language switch (%s)", expected_text
    )


@pytest.mark.parametrize("initial_locale, expected_new_locale", [
    ("en_US", "fr_FR"),  # Cycle forward
    ("fr_FR", "de_DE"),  # Cycle forward
    ("de_DE", "en_US"),  # Cycle wraps around (last to first)
])
def test_toggle_language_cycles_locale_and_refreshes_gui(_language_switch_builder, app_state_mock, simple_gui,
                                                         logger_mock, initial_locale, expected_new_locale):
    """
    Test the __toggle_language callback cycles the locale and triggers GUI refresh.
    """

    # Arrange: Set initial state and ensure button exists
    _language_switch_builder.build()
    app_state_mock.locale = initial_locale

    # Act
    _language_switch_builder._LanguageSwitchBuilder__toggle_language()  # noqa

    # Assert 1: The locale in app.state is updated
    assert app_state_mock.locale == expected_new_locale

    # Assert 2: The GUI is refreshed with the LanguageChange event
    simple_gui.refresh.assert_called_once_with(UIRefreshEvent.LanguageChange)

    # Assert 3: Logging is performed
    logger_mock.info.assert_any_call("Selected language - %s", expected_new_locale)
