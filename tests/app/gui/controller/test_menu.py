import pytest
from pytest_mock import MockerFixture

from tests.app.gui.controller import WidgetControllerTest


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

        from src.savegem import MenuController

        _mock_sections(_section_data)
        return MenuController(_widget_manager)

    @pytest.fixture
    def _change_tab_mock(self, mocker: MockerFixture, _controller):
        return mocker.patch.object(_controller, "_MenuController__change_tab")

    @pytest.fixture
    def _is_selected_mock(self, mocker: MockerFixture, _controller):
        return mocker.patch.object(_controller, "_MenuController__is_selected")

    def test_get_data(self, _controller, _section_data):
        controller_data = _controller._get_data()

        assert len(controller_data) == 2

        for row in range(0, len(controller_data)):
            assert controller_data[row].get("section_id") == _section_data[row].get("section_id")
            assert controller_data[row].get("section_label") == _section_data[row].get("section_label")
            assert controller_data[row].get("section_icon") == _section_data[row].get("section_icon")

    def test_refresh_when_no_current_section(self, mocker: MockerFixture, _controller, _change_tab_mock, _section_data):

        from src.savegem import TemplateWidgetController
        from src.savegem import MenuController

        parent_refresh_mock = mocker.patch.object(TemplateWidgetController, "refresh")
        parent_widget = mocker.MagicMock()

        _controller._set_state(MenuController.CurrentSection, None)
        _controller.refresh(parent_widget)

        parent_refresh_mock.assert_called_once()
        _change_tab_mock.assert_called_once_with(_section_data[0].get("section_id"))

    def test_refresh_when_current_section(self, mocker: MockerFixture, _controller, _change_tab_mock, _section_data):

        from src.savegem import TemplateWidgetController
        from src.savegem import MenuController

        parent_refresh_mock = mocker.patch.object(TemplateWidgetController, "refresh")
        parent_widget = mocker.MagicMock()

        _controller._set_state(MenuController.CurrentSection, "test_section")
        _controller.refresh(parent_widget)

        parent_refresh_mock.assert_called_once()
        _change_tab_mock.assert_not_called()

    def test_handle_menu_item(self, mocker: MockerFixture, _controller, _change_tab_mock, _is_selected_mock):

        from src.savegem import MenuController
        from src.savegem import QBool

        menu_item = mocker.MagicMock()
        _is_selected_mock.return_value = True

        _controller.handle__menu_item(menu_item, _controller.sections.rows[0])

        menu_item.setProperty.assert_called_once_with(MenuController.MenuItemActive, QBool(True))

        menu_item.reset_mock()
        _is_selected_mock.return_value = False
        _controller.handle__menu_item(menu_item, _controller.sections.rows[0])

        menu_item.setProperty.assert_called_once_with(MenuController.MenuItemActive, QBool(False))

        change_tab_callback = menu_item.clicked.connect.call_args[0][0]
        change_tab_callback()

        _change_tab_mock.assert_called_once_with(_controller.sections.get_first("section_id"))

    def test_resolve(self, _controller, _section_data, _is_selected_mock):

        section = _controller.sections.rows[0]
        expected_label = _controller.sections.get_first("section_label")
        expected_icon = _controller.sections.get_first("section_icon")

        _is_selected_mock.return_value = False

        label_result = _controller.resolve(section, "label")
        icon_result = _controller.resolve(section, "icon")
        invalid_result = _controller.resolve(section, "test")

        assert label_result == expected_label
        assert icon_result == expected_icon
        assert invalid_result is None

        # Check that section icon is being modified for selected section.
        _is_selected_mock.return_value = True

        icon_result = _controller.resolve(section, "icon")
        assert icon_result == f"active_{expected_icon}"

    def test_is_selected(self, _controller):

        from src.savegem import MenuController

        first_section = _controller.sections.rows[0]
        second_section = _controller.sections.rows[1]

        _controller._set_state(MenuController.CurrentSection, second_section.get("section_id"))

        assert _controller._MenuController__is_selected(first_section) is False  # noqa
        assert _controller._MenuController__is_selected(second_section) is True  # noqa

    def test_change_tab_early_exit(self, _controller, _widget_manager):
        """
        Tests that __change_tab returns early if the section ID is already the current state.
        """

        _controller._set_state(_controller.CurrentSection, "settings_section")
        _controller._MenuController__change_tab("settings_section")  # noqa

        _widget_manager.remove_widgets.assert_not_called()
        _widget_manager.build.assert_not_called()

    def test_change_tab_switch_flow(self, mocker: MockerFixture, _controller, _widget_manager,
                                    widget_section_build_command_mock):
        """
        Tests the core flow of tearing down the old UI and building the new section.
        """

        from src.savegem import UIRefreshEvent

        current_section_id = "home_section"
        new_section_id = "about_section"
        current_section_meta = mocker.MagicMock(section_id=current_section_id)
        new_section_meta = mocker.MagicMock(section_id=new_section_id)

        _controller._set_state(_controller.CurrentSection, current_section_id)
        _controller.sections.data.append(
            {"section_id": new_section_id, "section_label": "About", "section_icon": "about.svg"}
        )

        _controller._MenuController__change_tab(new_section_id)  # noqa

        assert _controller._get_state(_controller.CurrentSection) == new_section_id
        _widget_manager.delete.assert_called_once()
        delete_filter = _widget_manager.delete.call_args[0][0]
        assert delete_filter(current_section_meta) is True
        assert delete_filter(new_section_meta) is False

        widget_section_build_command_mock.assert_called_once_with(new_section_id)
        _widget_manager.execute.assert_called_once_with(widget_section_build_command_mock.return_value)

        _widget_manager.event_refresh.assert_called_once_with(UIRefreshEvent.MenuItemChanged)
        refresh_filter = _widget_manager.refresh.call_args[0][0]
        assert refresh_filter(current_section_meta) is False
        assert refresh_filter(new_section_meta) is True

        _widget_manager.enable.assert_called_once()
