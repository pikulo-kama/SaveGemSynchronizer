from unittest.mock import MagicMock, call, ANY
import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


@pytest.fixture
def mock_external_deps(mocker):
    """Mocks global singletons and utilities used across all controllers."""

    # Mock gui() and tr()
    mock_gui = MagicMock()
    mocker.patch('savegem.app.gui.controller.settings.gui', return_value=mock_gui)
    mocker.patch('savegem.app.gui.controller.settings.tr', side_effect=lambda k: f"TR({k})")

    # Mock app() state
    mock_app = MagicMock()
    mock_app.state.locale = "en_US"
    mock_app.state.time_format = TimeFormat.Regular
    mock_app.state.color_theme = ColorMode.Light  # Use a default for findData
    mocker.patch('savegem.app.gui.controller.settings.app', return_value=mock_app)

    # Mock database manager for language list
    mock_db = MagicMock()
    mock_db.retrieve_table.return_value = [
        {"locale_id": "en_US", "locale_name": "English"},
        {"locale_id": "fr_FR", "locale_name": "Français"},
    ]
    mocker.patch('savegem.app.gui.controller.settings.db', return_value=mock_db)

    # Mock file utilities
    mock_delete_file = mocker.patch('savegem.app.gui.controller.settings.delete_file')
    mock_resolve_app_data = mocker.patch('savegem.app.gui.controller.settings.resolve_app_data')

    # Mock sys.exit for LogoutController
    mock_exit = mocker.patch('savegem.app.gui.controller.settings.exit')

    return mock_app, mock_gui, mock_delete_file, mock_resolve_app_data, mock_exit


class SettingsControllerTestModuleHelper(WidgetControllerTest):

    @pytest.fixture(autouse=True)
    def _module_setup(self, app_state_mock):
        from src.savegem.constants import TimeFormat
        from src.savegem import ColorMode

        app_state_mock.locale = "en_US"
        app_state_mock.time_format = TimeFormat.Regular
        app_state_mock.color_theme = ColorMode.Light

    @pytest.fixture
    def _combobox(self, mocker: MockerFixture):
        return mocker.MagicMock()


class TestLanguageDropdownController(SettingsControllerTestModuleHelper):

    @pytest.fixture(autouse=True)
    def _setup(self, db_mock):
        from src.savegem import DatabaseRow

        db_mock.retrieve_table.return_value = [
            DatabaseRow(1, ("en_US", "English"), ["locale_id", "locale_name"]),
            DatabaseRow(1, ("fr_FR", "Français"), ["locale_id", "locale_name"])
        ]

    @pytest.fixture
    def _controller(self, _widget_manager):
        from src.savegem import LanguageDropdownController
        return LanguageDropdownController(_widget_manager)

    def test_setup_initializes_and_connects(self, _controller, _combobox, app_state_mock, db_mock):
        """
        Tests that setup loads locales from DB, adds items, sets current index, and connects signal.
        """

        _controller.setup(_combobox)

        db_mock.retrieve_table.assert_called_once_with("setup_locale")

        assert _combobox.addItem.call_count == 2
        _combobox.addItem.assert_any_call("English", "en_US")
        _combobox.addItem.assert_any_call("Français", "fr_FR")

        _combobox.findData.assert_called_once_with(app_state_mock.locale)
        _combobox.setCurrentIndex.assert_called_once()

        _combobox.currentIndexChanged.connect.assert_called_once()

    def test_on_language_change_updates_state(self, _controller, _widget_manager, _combobox, app_state_mock,
                                              gui_mock):
        """
        Tests the on_language_change callback correctly updates state and refreshes GUI.
        """

        from src.savegem import UIRefreshEvent

        # Setup mock return values for the callback logic
        _combobox.itemData.return_value = "de_DE"  # New locale ID

        _controller.setup(_combobox)

        # Get the callback function (index 5 is irrelevant, only itemData matters)
        on_language_change = _combobox.currentIndexChanged.connect.call_args[0][0]
        on_language_change(5)

        assert app_state_mock.locale == "de_DE"
        gui_mock.refresh.assert_called_once_with(UIRefreshEvent.LanguageChange)


class TestTimeFormatDropdownController(SettingsControllerTestModuleHelper):

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    @pytest.fixture
    def _controller(self, _widget_manager):
        from src.savegem import TimeFormatDropdownController
        return TimeFormatDropdownController(_widget_manager)

    def test_setup_initializes_and_connects(self, _controller, _combobox, app_state_mock):
        """
        Tests that setup adds two format options, sets current index, and connects signal.
        """

        from src.savegem.constants import TimeFormat

        _controller.setup(_combobox)

        # 1. Assert items added with translated text and correct data keys
        assert _combobox.addItem.call_count == 2
        _combobox.addItem.assert_any_call("Translated(label_TimeFormat12)", TimeFormat.Regular)
        _combobox.addItem.assert_any_call("Translated(label_TimeFormat24)", TimeFormat.Military)

        _combobox.setCurrentIndex.assert_called_once_with(app_state_mock.time_format)
        _combobox.currentIndexChanged.connect.assert_called_once()

    def test_on_time_format_change_updates_state(self, _widget_manager, _combobox, app_state_mock, _controller):
        """
        Tests the on_time_format_change callback correctly updates state.
        """

        from src.savegem.constants import TimeFormat

        # Setup mock return values for the callback logic
        _combobox.itemData.return_value = TimeFormat.Military

        _controller.setup(_combobox)

        on_time_format_change = _combobox.currentIndexChanged.connect.call_args[0][0]
        on_time_format_change(1)  # Simulate change to 24hr format

        assert app_state_mock.time_format == TimeFormat.Military

    def test_refresh_updates_item_text(self, _controller, _combobox):
        """
        Tests that refresh() updates the displayed text for localization.
        """

        _controller.refresh(_combobox)

        _combobox.setItemText.assert_has_calls([
            call(0, "Translated(label_TimeFormat12)"),
            call(1, "Translated(label_TimeFormat24)"),
        ])


class TestColorThemeDropdownController(SettingsControllerTestModuleHelper):

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    @pytest.fixture
    def _controller(self, _widget_manager):
        from src.savegem import ColorThemeDropdownController
        return ColorThemeDropdownController(_widget_manager)

    def test_setup_initializes_and_connects(self, _controller, _combobox, app_state_mock):
        """
        Tests that setup adds three color modes, sets index, and connects signal.
        """

        from src.savegem import ColorMode

        # Reset mock app state for this test
        app_state_mock.state.color_theme = ColorMode.Light

        _controller.setup(_combobox)

        # 1. Assert items added with correct data keys
        assert _combobox.addItem.call_count == 3
        _combobox.addItem.assert_any_call("Translated(label_ColorModeSystem)", None)
        _combobox.addItem.assert_any_call("Translated(label_ColorModeLight)", ColorMode.Light)
        _combobox.addItem.assert_any_call("Translated(label_ColorModeDark)", ColorMode.Dark)

        # 2. Assert current index set based on state
        _combobox.findData.assert_called_once_with(ColorMode.Light)
        _combobox.setCurrentIndex.assert_called_once()

        # 3. Assert signal connection
        _combobox.currentIndexChanged.connect.assert_called_once()

    def test_on_theme_change_updates_gui_and_refreshes_manager(self, _controller, _widget_manager, _combobox,
                                                               app_state_mock, gui_mock):
        """
        Tests the callback updates state, reloads styles, and triggers manager refresh.
        """

        from src.savegem import ColorMode

        # Setup mock return values for the callback logic
        _combobox.itemData.return_value = ColorMode.Dark

        _controller.setup(_combobox)

        on_theme_change = _combobox.currentIndexChanged.connect.call_args[0][0]
        on_theme_change(2)  # Simulate change to Dark mode

        assert app_state_mock.color_theme == ColorMode.Dark
        gui_mock.reload_styles.assert_called_once()
        _widget_manager.refresh.assert_called_once()

    def test_refresh_updates_item_text(self, _controller, _combobox):
        """
        Tests that refresh() updates the displayed text for localization.
        """

        _controller.refresh(_combobox)

        _combobox.setItemText.assert_has_calls([
            call(0, "Translated(label_ColorModeSystem)"),
            call(1, "Translated(label_ColorModeLight)"),
            call(2, "Translated(label_ColorModeDark)"),
        ])


class TestLogoutController(SettingsControllerTestModuleHelper):

    @pytest.fixture(autouse=True)
    def _setup(self, tr_mock):
        pass

    @pytest.fixture
    def _controller(self, _widget_manager):
        from src.savegem import LogoutController
        return LogoutController(_widget_manager)

    @pytest.fixture
    def _logout_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    def test_setup_connects_to_confirmation_dialog(self, _controller, _logout_button, gui_mock):
        """
        Tests that setup connects the button click to the gui().confirmation wrapper.
        """
        _controller.setup(_logout_button)

        # 1. Assert connection
        _logout_button.clicked.connect.assert_called_once()
        outer_callback = _logout_button.clicked.connect.call_args[0][0]

        # 2. Simulate click (runs the outer wrapper)
        outer_callback()

        # 3. Assert confirmation called with correct message and inner callback
        gui_mock.confirmation.assert_called_once_with("Translated(confirmation_ConfirmLogout)", ANY)

    def test_logout_callback_cleans_up_and_exits(self, _controller, _logout_button, _widget_manager, gui_mock,
                                                 delete_file_mock, resolve_app_data_mock, sys_exit_mock):
        """
        Tests the core logout logic: file deletion, GUI destruction, and program exit.
        """

        from src.savegem.constants import File

        # Set up the expected app data path
        resolve_app_data_mock.return_value = "/mock/auth/token.dat"

        _controller.setup(_logout_button)

        outer_callback = _logout_button.clicked.connect.call_args[0][0]
        outer_callback()

        # Get the inner logout function (we have to manually construct the confirmation wrapper)
        inner_logout_func = gui_mock.confirmation.call_args[0][1]
        inner_logout_func()

        # 1. Assert file deletion was attempted using resolved path
        resolve_app_data_mock.assert_called_once_with(File.GDriveToken)
        delete_file_mock.assert_called_once_with("/mock/auth/token.dat")

        # 2. Assert GUI destruction
        gui_mock.destroy.assert_called_once()

        # 3. Assert program exit
        sys_exit_mock.assert_called_once_with(0)
