import pytest
from unittest.mock import MagicMock, call, ANY
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


@pytest.fixture
def mock_external_utils(mocker):
    """Mocks global utilities."""
    mocker.patch('savegem.app.gui.controller.menu.resolve_content',
                 side_effect=lambda s: f"RESOLVED({s})")
    mocker.patch('savegem.app.gui.controller.menu.resolve_resource',
                 side_effect=lambda s: f"/resources/{s}")
    mocker.patch('savegem.app.gui.controller.menu._logger', MagicMock())

    # Mock QIcon to prevent PyQt type errors (though usually not necessary with MagicMock)
    mocker.patch('savegem.app.gui.controller.menu.QIcon', return_value=MagicMock(spec=QIcon))

class TestMenuController(WidgetControllerTest):

    @pytest.fixture
    def _section_data(self):
        """
        Provides mock section data for the menu.
        """

        return [
            {"section_id": "home_section", "section_label": "Home", "section_icon": "home.svg"},
            {"section_id": "settings_section", "section_label": "Settings", "section_icon": "settings.svg"},
        ]

    @pytest.fixture
    def _controller(self, _widget_manager, _mock_sections, _section_data):
        """
        Provides the MenuController instance with mocked dependencies.
        """

        from savegem.app.gui.controller.menu import MenuController

        _mock_sections(_section_data)
        return MenuController(_widget_manager)

    @pytest.fixture
    def _home_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _settings_button(self, mocker: MockerFixture):
        return mocker.MagicMock()

    @pytest.fixture
    def _menu(self, mocker: MockerFixture, _home_button, _settings_button, _push_button_mock):
        """
        Mocks the QWidget instance passed as the menu, including its layout and button finding.
        """

        mock_menu = mocker.MagicMock()
        mock_menu.findChild.side_effect = lambda _, key: {
            "home_section": _home_button,
            "settings_section": _settings_button
        }.get(key)

        _push_button_mock.side_effect = [_home_button, _settings_button]

        return mock_menu

    def test_setup_initializes_buttons(self, mocker: MockerFixture, _controller, _menu, _section_data,
                                       _push_button_mock, _spacer_mock, _home_button, _settings_button):
        """
        Tests that setup creates a button for each section, connects signals, and triggers initial load.
        """

        change_tab_mock = mocker.patch.object(_controller, "_MenuController__change_tab")
        layout_mock = _menu.layout.return_value

        _controller.setup(_menu)

        # 1. Assert buttons were created (one for each section)
        assert _push_button_mock.call_count == 2

        # Check properties set
        _home_button.setObjectName.assert_called_once_with("home_section")
        _settings_button.setObjectName.assert_called_once_with("settings_section")

        # Check icon size
        _home_button.setIconSize.assert_called_once_with(QSize(25, 25))

        # Check signal connection
        _home_button.clicked.connect.assert_called_once()

        # 3. Assert spacer and buttons added to layout
        layout_mock.add_dynamic_widget.assert_has_calls([
            call(_home_button),
            call(_settings_button)
        ], any_order=True)

        layout_mock.addWidget.assert_called_once_with(_spacer_mock.return_value)

        # 4. Assert initial tab change triggered for the first section
        change_tab_mock.assert_called_once_with("home_section")

    def test_refresh_updates_buttons_correctly(self, module_patch, _controller, _menu, _section_data, _settings_button,
                                               _home_button, resolve_content_mock, resolve_resource_mock):
        """
        Tests that refresh() updates icons, tooltips, and 'active' property based on state.
        """

        from savegem.app.gui.constants import QBool

        module_patch("QIcon", side_effect=lambda path: path)
        resolve_resource_mock.side_effect = lambda path: f"/resources/{path}"

        _controller._set_state(_controller.CurrentSection, "settings_section")
        _controller.refresh(_menu)

        _settings_button.setToolTip.assert_called_once_with("RESOLVED(Settings)")
        # We only check QIcon type, content is checked by resolved string
        _settings_button.setIcon.assert_called_once_with(ANY)

        # Check resolved resource path for active icon
        _settings_button.setIcon.assert_called_once_with("/resources/active_settings.svg")
        _settings_button.setProperty.assert_called_once_with("active", QBool(True))

        # Assertions on the HOME button mock ('home_section', icon: 'home.svg')
        _home_button.setToolTip.assert_called_once_with("RESOLVED(Home)")
        _home_button.setIcon.assert_called_once_with(ANY)

        # Check resolved resource path for normal icon
        _home_button.setIcon.assert_called_once_with("/resources/home.svg")
        _home_button.setProperty.assert_called_once_with("active", QBool(False))

    def test_change_tab_early_exit(self, _controller, _widget_manager):
        """
        Tests that __change_tab returns early if the section ID is already the current state.
        """

        _controller._set_state(_controller.CurrentSection, "settings_section")
        _controller._MenuController__change_tab("settings_section")  # noqa

        _widget_manager.remove_widgets.assert_not_called()
        _widget_manager.build.assert_not_called()

    def test_change_tab_switch_flow(self, _controller, _widget_manager):
        """
        Tests the core flow of tearing down the old UI and building the new section.
        """

        new_section_id = "about_section"

        _controller._set_state(_controller.CurrentSection, "home_section")
        _controller.sections.data.append(
            {"section_id": new_section_id, "section_label": "About", "section_icon": "about.svg"}
        )

        _controller._MenuController__change_tab(new_section_id)  # noqa

        assert _controller._get_state(_controller.CurrentSection) == new_section_id
        _widget_manager.remove_widgets.assert_called_once()
        _widget_manager.build.assert_called_once_with(new_section_id)
        _widget_manager.refresh.assert_called_once()
        _widget_manager.enable.assert_called_once()